import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from config.ModelConfig import ModelConfig
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

class LLMService:
    
    def __init__(self):
        self.model_name = ModelConfig.EMBEDDING_MODEL
        self.fallback_model = ModelConfig.FALLBACK_MODEL
        self.model = self._initialize_llm()
        
    
    def _initialize_llm(self):
        """Initialize the LLM"""
        try:
            if self.model_name == None:
                raise ValueError
            print(f"Loading model: {self.model_name}")
            
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                dtype=torch.bfloat16,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=100,
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
            
            llm = HuggingFacePipeline(pipeline=pipe)
            chat_model = ChatHuggingFace(llm=llm)
            print(f"Model {self.model_name} loaded successfully!")
            return chat_model
            
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            print("Falling back to simpler model...")
            
            try:
                print(f"Trying fallback model: {self.fallback_model}")
                
                tokenizer = AutoTokenizer.from_pretrained(self.fallback_model)
                model = AutoModelForCausalLM.from_pretrained(str(self.fallback_model))
                
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=50,
                    temperature=0.7
                )
                
                llm = HuggingFacePipeline(pipeline=pipe)
                chat_model = ChatHuggingFace(llm=llm)
                print("Fallback model loaded successfully!")
                return chat_model
                
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                print("Using rule-based fallback system.")
                return None