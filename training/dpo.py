"""DPO preference alignment starter. JSONL fields: prompt, chosen, rejected."""
import argparse, torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig
from trl import DPOTrainer, DPOConfig

def main():
    p=argparse.ArgumentParser(); p.add_argument("--model",required=True); p.add_argument("--data",default="data/training/triage_preferences.jsonl"); p.add_argument("--out",default="artifacts/triage-dpo"); a=p.parse_args()
    if not torch.cuda.is_available(): raise RuntimeError("DPO fine-tuning requires CUDA for this configuration.")
    ds=load_dataset("json",data_files=a.data,split="train")
    if len(ds)<500: raise ValueError(f"Need at least 500 preference pairs; found {len(ds)}")
    tok=AutoTokenizer.from_pretrained(a.model); tok.pad_token=tok.eos_token
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_compute_dtype=torch.float16)
    model=AutoModelForCausalLM.from_pretrained(a.model,quantization_config=q,device_map="auto")
    cfg=DPOConfig(output_dir=a.out,per_device_train_batch_size=1,gradient_accumulation_steps=8,num_train_epochs=1,learning_rate=5e-5,fp16=True)
    trainer=DPOTrainer(model=model,args=cfg,train_dataset=ds,processing_class=tok,peft_config=LoraConfig(r=16,lora_alpha=32,task_type="CAUSAL_LM"))
    trainer.train(); trainer.save_model(a.out)
if __name__=="__main__": main()
