from typing import List, Dict, Any
from tqdm import tqdm
from .base_evaluator import BaseEvaluator
from ..utils.prompt_utils import load_prompt
from ..utils.data_utils import save_agent_data
from ..utils.mcq_utils import extract_option_letters_from_options_text, parse_mcq_prediction
from ..utils.image_utils import is_url, load_image_base64

class MultimodalEvaluator(BaseEvaluator):
    """
    Evaluator for multimodal tasks (image + text), e.g. Image QA, Image MCQ.
    """
    
    def evaluate_multiple_choice(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate multimodal multiple choice questions.
        """
        prompt_template = load_prompt(f"multiple_choice_{self.lang}.txt")
        
        correct_count = 0
        results = []
        
        for idx, item in enumerate(tqdm(dataset, desc="Evaluating Multimodal MCQ")):
            question = item.get("question", "")
            options = item.get("options", "")
            image_url = item.get("image_url", "")
            ground_truth = item.get("answer", "").strip().upper()
            
            prompt_text = prompt_template.format(question=question, options=options)

            model_name = self.model.__class__.__name__
            if model_name in {"OpenAIModel", "GeneralOpenAICompatibleModel"}:
                if is_url(image_url):
                    image_ref = image_url
                else:
                    b64, media_type = load_image_base64(image_url)
                    image_ref = f"data:{media_type};base64,{b64}"
                content = [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": image_ref}},
                ]
                messages = [{"role": "user", "content": content}]
            elif model_name == "ClaudeModel":
                b64, _ = load_image_base64(image_url)
                content = [
                    {"text": prompt_text},
                    {"image": b64},
                ]
                messages = [{"role": "user", "content": content}]
            else:
                content = [
                    {"text": prompt_text},
                    {"image": image_url}
                ]
                messages = [{"role": "user", "content": content}]
            
            response = self.model.generate(messages, max_tokens=1024)
            
            valid_letters = extract_option_letters_from_options_text(options)
            predicted = parse_mcq_prediction(response, valid_options=valid_letters)
            
            is_correct = (predicted == ground_truth)
            if is_correct:
                correct_count += 1
                
            results.append({
                "id": idx,
                "question": question,
                "image_url": image_url,
                "predicted": predicted,
                "ground_truth": ground_truth,
                "is_correct": is_correct,
                "raw_response": response
            })
            
        accuracy = correct_count / len(dataset) if dataset else 0.0
        
        summary = {
            "accuracy": accuracy,
            "total": len(dataset),
            "correct": correct_count,
            "details": results
        }
        
        save_agent_data(summary, task_name="multimodal_mcq_evaluation")
        return summary
        
    def evaluate_open_qa(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate Multimodal Open QA.
        """
        prompt_template = load_prompt(f"open_qa_{self.lang}.txt")
        
        results = []
        
        for idx, item in enumerate(tqdm(dataset, desc="Evaluating Multimodal Open QA")):
            question = item.get("question", "")
            image_url = item.get("image_url", "")
            
            prompt_text = prompt_template.format(question=question)
            model_name = self.model.__class__.__name__
            if model_name in {"OpenAIModel", "GeneralOpenAICompatibleModel"}:
                if is_url(image_url):
                    image_ref = image_url
                else:
                    b64, media_type = load_image_base64(image_url)
                    image_ref = f"data:{media_type};base64,{b64}"
                content = [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": image_ref}},
                ]
                messages = [{"role": "user", "content": content}]
            elif model_name == "ClaudeModel":
                b64, _ = load_image_base64(image_url)
                content = [
                    {"text": prompt_text},
                    {"image": b64},
                ]
                messages = [{"role": "user", "content": content}]
            else:
                content = [
                    {"text": prompt_text},
                    {"image": image_url}
                ]
                messages = [{"role": "user", "content": content}]
            
            response = self.model.generate(messages, max_tokens=1024)
            
            results.append({
                "id": idx,
                "question": question,
                "image_url": image_url,
                "ground_truth": item.get("answer", ""),
                "ai_answer": response
            })
            
        summary = {
            "total": len(dataset),
            "details": results
        }
        
        save_agent_data(summary, task_name="multimodal_open_qa_generation")
        return summary
        
    def evaluate(self, dataset: List[Dict[str, Any]], task_type: str = "multiple_choice") -> Dict[str, Any]:
        if task_type == "multiple_choice":
            return self.evaluate_multiple_choice(dataset)
        elif task_type == "open_qa":
            return self.evaluate_open_qa(dataset)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
