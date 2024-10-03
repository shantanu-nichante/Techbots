from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pytesseract
from PIL import Image
import os

# ... existing analyze_ingredients function ...

def index(request):
    return render(request, 'index.html')



def analyze_ingredients(ingredients):
    unhealthy = {
        "Sugar": "Excess sugar can lead to weight gain and diabetes",
        "Hydrogenated Vegetable Oil": "Increases bad cholesterol, risk of heart disease",
        "Monosodium Glutamate": "Can cause headaches and other reactions in sensitive individuals",
    }
    healthy = {
        "Rice": "Good source of energy and essential nutrients.",
        "Onion": "Rich in antioxidants and has anti-inflammatory properties.",
        "Tomato": "Rich in vitamins and antioxidants.",
    }

    found_unhealthy = {ingredient: unhealthy[ingredient] for ingredient in unhealthy if ingredient in ingredients}
    found_healthy = {ingredient: healthy[ingredient] for ingredient in healthy if ingredient in ingredients}

    return found_unhealthy, found_healthy


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)
        
        file = request.FILES['file']
        if file.name == '':
            return JsonResponse({"error": "No selected file"}, status=400)
        
        if file:
            # Save the uploaded file
            file_path = default_storage.save('upload/' + file.name, ContentFile(file.read()))
            file_path = os.path.join(default_storage.location, file_path)

            # Perform OCR to extract text from the image
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img)

            # Analyze the ingredients
            ingredients = extracted_text.split(',')
            unhealthy, healthy = analyze_ingredients([ingredient.strip() for ingredient in ingredients])

            # Prepare the response
            response = {
                "unhealthy": unhealthy,
                "healthy": healthy
            }

            return JsonResponse(response)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# Remove the Flask app.run() part