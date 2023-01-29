import os
from math import ceil
from multiprocessing import Lock
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

class Predictor(object):
    """
    Main class for generating predictions based on transformers models.
    """
    def __init__(self) -> None:
        """
        Instantiate models on correct devices and configure it to worker with multiprocessing
        """
        self.lock = Lock()
        self.device = "cpu"
        self.batch_size = int(os.getenv("BATCH_SIZE", 2))

        weights = os.getenv("MODEL_WEIGHTS", "facebook/m2m100_418M")
        self.model = M2M100ForConditionalGeneration.from_pretrained(weights)
        self.tokenizer = M2M100Tokenizer.from_pretrained(weights)

        if torch.cuda.is_available():
            self.device = "cuda"
            self.model.to(self.device)
            self.model.share_memory()
            torch.set_num_threads(1)
        self.model.eval()
        
        self.build()
    
    def save(self):
        """
        Save model weights to specific location for posterior use
        """
        save_path = os.getenv("SAVE_WEIGHTS")
        if save_path:
            self.model.save_pretrained(save_path)
            self.tokenizer.save_pretrained(save_path)

    def build(self):
        """
        Perform test inference to guarantee model is loaded and ready
        """
        result = self.predict(texts=["test"], src_lang="en", tgt_lang="ja")
        print("Model has been loaded and is ready for use.")
    
    def predict(self, texts:list, src_lang:str, tgt_lang:str):
        """
        Perform inference on a batch of text inputs. Batch is limited to interval [1,BATCH_SIZE]
        """
        with self.lock:
            self.tokenizer.src_lang = src_lang
            model_inputs = self.tokenizer(texts, return_tensors="pt").to(self.device)
        generated_tokens = self.model.generate(**model_inputs, forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang)).to("cpu")
        result = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        return result

    def get_predictions(self, records:list, src_lang:str, tgt_lang:str):
        """
        Preprocess inputs, perform batch inference and arrange results.
        """
        results = []
        ids = list(map(lambda r: r.id, records))
        txts = list(map(lambda r: r.text, records))
        for batch_id in range(ceil(len(txts)/self.batch_size)):
            batch_ids = ids[batch_id*self.batch_size:(batch_id+1)*self.batch_size]
            batch_txts = txts[batch_id*self.batch_size:(batch_id+1)*self.batch_size]
            preds = self.predict(batch_txts, src_lang, tgt_lang)
            results.extend([*map(lambda r: {"id":r[0], "text":r[1]}, zip(batch_ids, preds))])
        if self.device == "cuda":
            torch.cuda.empty_cache()
        return results

if __name__ == "__main__":
    records = [
        "Life is like a box of chocolates."
    ]
    src_lang = "en"
    tgt_lang = "ja"
    model = Predictor()
    results = model.predict(records, src_lang, tgt_lang)
    model.save()
    