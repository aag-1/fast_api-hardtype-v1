from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import time
from random_word import RandomWords
from pydantic import BaseModel
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

r = RandomWords()

class TypingResult(BaseModel):
    wpm: float
    adjusted_score: float
    adjusted_error: float

def generate_words() -> str:
    return " ".join([r.get_random_word() for _ in range(15)])

def calculate_wpm_and_score(input_text: str, generated_words: List[str], typing_duration: float) -> TypingResult:
    score = 0
    error = 0

    input_words = input_text.split()
    outputchecktext = "".join(generated_words)
    usertypechecktext = "".join(input_text.split())

    numbernotwritten = len(generated_words) - len(input_words)

    txtoutputreformed = outputchecktext[:len(usertypechecktext)]

    for i in range(len(txtoutputreformed)):
        if txtoutputreformed[i] == usertypechecktext[i]:
            score += 1
        else:
            error += 1

    score1 = 0
    error1 = 0

    for i in range(len(generated_words)):
        if i < len(input_words):
            word1 = generated_words[i]
            word2 = input_words[i]

            min_len = min(len(word1), len(word2))
            for k in range(min_len):
                if word1[k] == word2[k]:
                    score1 += 1
                else:
                    error1 += 1

            if len(word1) != len(word2):
                error1 += abs(len(word1) - len(word2))

    adjusted_score = (score1 + score) / 2
    adjusted_error = (error1 + error + numbernotwritten) / 3

    numerator = (adjusted_score - adjusted_error)
    denominator = (typing_duration * numbernotwritten) / 60
    wpm = numerator / denominator if denominator > 0 else 0

    return TypingResult(wpm=round(wpm, 2), adjusted_score=round(adjusted_score, 2), adjusted_error=round(adjusted_error, 2))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    words = generate_words()
    return templates.TemplateResponse("index.html", {"request": request, "words": words})

@app.post("/", response_class=HTMLResponse)
async def handle_typing(
    request: Request,
    input_text: str = Form(...),
    start_time: float = Form(...),
    words: str = Form(...)
):
    end_time = time.time()
    typing_duration = end_time - start_time
    word_list = words.split()

    result = calculate_wpm_and_score(input_text, word_list, typing_duration)
    
    new_words = generate_words()
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "words": new_words,
            "wpm": result.wpm,
            "adjusted_score": result.adjusted_score,
            "adjusted_error": result.adjusted_error
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)