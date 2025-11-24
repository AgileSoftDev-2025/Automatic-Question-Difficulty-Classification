import pandas as pd
import torch
from transformers import (
    T5ForConditionalGeneration, 
    AutoTokenizer,
    TrainingArguments, 
    Trainer,
    DataCollatorForSeq2Seq
)
from datasets import Dataset
from sklearn.model_selection import train_test_split
import numpy as np

class BloomQuestionTransformer:
    def __init__(self, model_name="t5-base"):
        """
        Initialize the Bloom Taxonomy Question Transformer
        
        Args:
            model_name: Base model to use (t5-base, t5-large, or facebook/bart-base)
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        
    def prepare_dataset_from_csv(self, csv_path):
        """
        Prepare training dataset from your CSV format
        Assumes CSV has columns: C1, C2, C3, C4, C5, C6
        Each row represents one topic with questions at all levels
        
        Args:
            csv_path: Path to your CSV file
            
        Returns:
            Dataset object ready for training
        """
        df = pd.read_csv(csv_path)
        
        training_data = []
        bloom_levels = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        
        # For each row (topic), create all possible transformations
        for idx, row in df.iterrows():
            for source_level in bloom_levels:
                for target_level in bloom_levels:
                    if source_level != target_level:
                        source_question = row[source_level]
                        target_question = row[target_level]
                        
                        # Skip if any question is missing
                        if pd.isna(source_question) or pd.isna(target_question):
                            continue
                        
                        # Create input format: "transform C1 to C3: [question]"
                        input_text = f"transform {source_level} to {target_level}: {source_question}"
                        
                        training_data.append({
                            'input_text': input_text,
                            'target_text': target_question,
                            'source_level': source_level,
                            'target_level': target_level
                        })
        
        print(f"Created {len(training_data)} training examples from {len(df)} topics")
        return training_data
    
    def preprocess_function(self, examples):
        """Tokenize the inputs and targets"""
        model_inputs = self.tokenizer(
            examples['input_text'],
            max_length=512,
            truncation=True,
            padding='max_length'
        )
        
        labels = self.tokenizer(
            examples['target_text'],
            max_length=512,
            truncation=True,
            padding='max_length'
        )
        
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    
    def train(self, csv_path, output_dir="./bloom_transformer_model", 
              epochs=10, batch_size=8, learning_rate=5e-5):
        """
        Train the model on your dataset
        
        Args:
            csv_path: Path to your CSV file
            output_dir: Directory to save the trained model
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for optimizer
        """
        # Prepare data
        training_data = self.prepare_dataset_from_csv(csv_path)
        
        # Split into train and validation
        train_data, val_data = train_test_split(training_data, test_size=0.1, random_state=42)
        
        # Convert to HuggingFace Dataset
        train_dataset = Dataset.from_list(train_data)
        val_dataset = Dataset.from_list(val_data)
        
        # Tokenize
        train_dataset = train_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=['input_text', 'target_text', 'source_level', 'target_level']
        )
        val_dataset = val_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=['input_text', 'target_text', 'source_level', 'target_level']
        )
        
        # Initialize model
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
        self.model.to(self.device)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            push_to_hub=False,
            logging_steps=100,
            warmup_steps=500,
            fp16=torch.cuda.is_available(),
        )
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            self.tokenizer,
            model=self.model,
            padding=True
        )
        
        # Initialize Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
        )
        
        # Train
        print("Starting training...")
        trainer.train()
        
        # Save final model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        print(f"Model saved to {output_dir}")
        
    def load_model(self, model_path):
        """Load a trained model from disk"""
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        print(f"Model loaded from {model_path}")
        
    def transform_question(self, question, source_level, target_level, 
                          max_length=512, num_beams=5, temperature=0.7):
        """
        Transform a question from one Bloom level to another
        
        Args:
            question: The input question
            source_level: Current Bloom level (C1-C6)
            target_level: Desired Bloom level (C1-C6)
            max_length: Maximum length of generated text
            num_beams: Number of beams for beam search
            temperature: Sampling temperature (lower = more deterministic)
            
        Returns:
            Transformed question
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call train() or load_model() first.")
        
        # Prepare input
        input_text = f"transform {source_level} to {target_level}: {question}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                temperature=temperature,
                early_stopping=True,
                do_sample=False  # Use beam search for better quality
            )
        
        # Decode
        transformed_question = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return transformed_question
    
    def batch_transform(self, questions, source_levels, target_levels):
        """
        Transform multiple questions at once
        
        Args:
            questions: List of questions
            source_levels: List of source levels
            target_levels: List of target levels
            
        Returns:
            List of transformed questions
        """
        results = []
        for q, src, tgt in zip(questions, source_levels, target_levels):
            transformed = self.transform_question(q, src, tgt)
            results.append(transformed)
        return results


# Example usage
if __name__ == "__main__":
    # Initialize transformer
    transformer = BloomQuestionTransformer(model_name="t5-base")
    
    # Train on your dataset
    transformer.train(
        csv_path="dataset sample.csv",
        output_dir="./bloom_model",
        epochs=10,
        batch_size=4
    )
    
    # Load a pre-trained model
    # transformer.load_model("./bloom_model")
    
    # Transform a question
    original = "Define what 'traumatic memory' means in cultural studies."
    transformed = transformer.transform_question(
        question=original,
        source_level="C1",
        target_level="C3"
    )
    print(f"Original (C1): {original}")
    print(f"Transformed (C3): {transformed}")