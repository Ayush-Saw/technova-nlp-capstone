"""QLoRA SFT starter. Run on a compatible CUDA host; model licence/revision must be recorded."""
import argparse, os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model",required=True); p.add_argument("--data",default="data/training/triage_sft.jsonl")
    p.add_argument("--out",default="artifacts/triage-sft"); args=p.parse_args()
    if not __import__("torch").cuda.is_available(): raise RuntimeError("QLoRA training requires a compatible CUDA GPU.")
    ds=load_dataset("json",data_files=args.data,split="train")
    tok=AutoTokenizer.from_pretrained(args.model); tok.pad_token=tok.eos_token
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_compute_dtype=__import__("torch").float16)
    model=AutoModelForCausalLM.from_pretrained(args.model,quantization_config=q,device_map="auto")
    model=prepare_model_for_kbit_training(model)
    model.config.use_cache=False
    peft=LoraConfig(r=16,lora_alpha=32,lora_dropout=0.05,bias="none",task_type="CAUSAL_LM",target_modules="all-linear")
    def fmt(x): return f"Instruction: Classify this support ticket. Return JSON only.\nTicket: {x['ticket']}\nJSON: {x['completion']}"
    args_train=TrainingArguments(output_dir=args.out,per_device_train_batch_size=1,gradient_accumulation_steps=8,
        learning_rate=2e-4,num_train_epochs=2,logging_steps=10,save_strategy="epoch",fp16=True,report_to=["mlflow"])
    trainer=SFTTrainer(model=model,args=args_train,train_dataset=ds,peft_config=peft,formatting_func=fmt)
    trainer.train(); trainer.save_model(args.out); tok.save_pretrained(args.out)
if __name__=="__main__": main()
