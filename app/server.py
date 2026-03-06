"""
Flask API for pet disease prediction.
"""

import os
import joblib
import numpy as np
from flask import Flask, request, jsonify, render_template

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)

# ── Load model artifacts ──────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "pet_disease_model.pkl")
artifacts = joblib.load(MODEL_PATH)
model = artifacts["model"]
label_encoder = artifacts["label_encoder"]
feature_names = artifacts["feature_names"]
symptom_cols = artifacts["symptom_cols"]


# Disease descriptions for UI
DISEASE_INFO = {
    "Parvovirus": {
        "description": "A highly contagious viral disease in dogs causing severe GI symptoms. Seek emergency vet care.",
        "remedies": "Immediate intensive care by a veterinarian (IV fluids, anti-nausea medication). Do not attempt home treatment.",
        "emergency": True
    },
    "Canine Distemper": {
        "description": "A serious viral illness affecting the respiratory, GI, and nervous systems.",
        "remedies": "Requires strict veterinary support. Keep the dog isolated, warm, and hydrated.",
        "emergency": True
    },
    "Kennel Cough": {
        "description": "A contagious respiratory disease. Usually mild but can need treatment in puppies.",
        "remedies": "Rest, use a humidifier, keep away from smoke/dust. Cough suppressants may be prescribed by a vet.",
        "emergency": False
    },
    "Canine Hip Dysplasia": {
        "description": "A genetic skeletal condition where the hip joint doesn't develop properly.",
        "remedies": "Weight management, joint supplements (glucosamine), physical therapy. Surgery in severe cases.",
        "emergency": False
    },
    "Canine Heartworm": {
        "description": "Parasitic worms living in the heart and lungs. Preventable with monthly medication.",
        "remedies": "Requires specialized vet treatment protocol to kill worms safely. Strict rest is mandatory.",
        "emergency": True
    },
    "Canine Leptospirosis": {
        "description": "A bacterial infection that can damage the liver and kidneys. Treatable with antibiotics.",
        "remedies": "Veterinary prescribed antibiotics, IV fluids. Ensure strict hygiene as it's transmissible to humans.",
        "emergency": True
    },
    "Canine Bloat (GDV)": {
        "description": "A life-threatening condition where the stomach twists. Requires emergency surgery.",
        "remedies": "Immediate surgical intervention is required. No home remedies.",
        "emergency": True
    },
    "Canine Arthritis": {
        "description": "Joint inflammation causing pain and stiffness, common in older dogs.",
        "remedies": "Weight control, orthopedic beds, moderate exercise, and vet-prescribed pain management/supplements.",
        "emergency": False
    },
    "Canine Mange": {
        "description": "A skin disease caused by mites leading to itching and hair loss.",
        "remedies": "Medicated baths and specific anti-mite treatments prescribed by a vet. Regular cleaning of bedding.",
        "emergency": False
    },
    "Canine Ear Infection": {
        "description": "Inflammation of the ear canal, often caused by bacteria or yeast.",
        "remedies": "Cleaning with vet-approved ear cleansers, followed by prescribed antibiotic or antifungal drops.",
        "emergency": False
    },
    "Canine UTI": {
        "description": "Urinary tract infection causing frequent, painful urination.",
        "remedies": "Veterinary antibiotics are necessary. Encourage increased water intake.",
        "emergency": False
    },
    "Canine Obesity": {
        "description": "Excessive weight that can lead to other health problems. Managed through diet and exercise.",
        "remedies": "Portion control, specialized weight-loss diet, and gradually increasing daily exercise.",
        "emergency": False
    },
    "Canine Diabetes": {
        "description": "A metabolic disorder affecting blood sugar regulation. Requires ongoing management.",
        "remedies": "Daily insulin injections and a strict, consistent diet as prescribed by a veterinarian.",
        "emergency": False
    },
    "Canine Allergies": {
        "description": "Immune reactions to environmental or food allergens causing skin and respiratory issues.",
        "remedies": "Identify and remove allergens. Vet-prescribed antihistamines or specialty diets may help.",
        "emergency": False
    },
    "Rabies (Dog)": {
        "description": "A fatal viral disease affecting the nervous system. Preventable by vaccination.",
        "remedies": "No cure exists once symptoms appear. It is legally mandated to report suspected cases. Euthanasia is typically required.",
        "emergency": True
    },
    "Feline Upper Respiratory Infection": {
        "description": "Common cold-like illness in cats. Usually resolves with supportive care.",
        "remedies": "Keep face clean, provide highly aromatic foods if smell is affected, use a humidifier. Antibiotics if bacterial.",
        "emergency": False
    },
    "Feline Panleukopenia": {
        "description": "A highly contagious and deadly viral disease in cats. Vaccination is critical.",
        "remedies": "Requires aggressive inpatient veterinary care (IV fluids, antibiotics to prevent secondary infections).",
        "emergency": True
    },
    "Feline Leukemia (FeLV)": {
        "description": "A retrovirus that suppresses the immune system. No cure but manageable.",
        "remedies": "Keep indoors, provide a stress-free environment, high-quality diet, and regular vet checkups.",
        "emergency": False
    },
    "Feline Immunodeficiency Virus (FIV)": {
        "description": "A slow-acting virus similar to HIV. Cats can live normal lives with care.",
        "remedies": "Keep strictly indoors to prevent transmission and secondary infections. Feed a balanced diet.",
        "emergency": False
    },
    "Feline Diabetes": {
        "description": "Blood sugar regulation disorder. May require insulin injections.",
        "remedies": "Low-carbohydrate, high-protein diet, and insulin therapy overseen by a vet.",
        "emergency": False
    },
    "Feline Hyperthyroidism": {
        "description": "Overactive thyroid gland causing weight loss despite increased appetite.",
        "remedies": "Medication (methimazole), radioactive iodine therapy, or specialized diets as directed by a vet.",
        "emergency": False
    },
    "Feline Kidney Disease": {
        "description": "Progressive loss of kidney function, common in older cats.",
        "remedies": "Specialized renal diets, increased water availability (water fountains), subcutaneous fluids.",
        "emergency": False
    },
    "Feline Lower Urinary Tract Disease (FLUTD)": {
        "description": "A group of conditions affecting the bladder and urethra.",
        "remedies": "Increase water intake, feed wet food, reduce stress. Seek immediate vet care if straining to urinate (possible blockage).",
        "emergency": True
    },
    "Feline Ringworm": {
        "description": "A fungal skin infection causing circular patches of hair loss.",
        "remedies": "Topical antifungal treatments and environmental decontamination. Wash hands thoroughly.",
        "emergency": False
    },
    "Feline Ear Mites": {
        "description": "Tiny parasites in the ear canal causing intense itching.",
        "remedies": "Thorough ear cleaning followed by specific anti-mite medications prescribed by a vet.",
        "emergency": False
    },
    "Feline Asthma": {
        "description": "Chronic inflammation of the airways causing coughing and breathing difficulty.",
        "remedies": "Avoid irritants (smoke, dusty litter), use vet-prescribed inhalers or oral medications.",
        "emergency": False # Note: Acute attacks are emergencies
    },
    "Feline Inflammatory Bowel Disease": {
        "description": "Chronic inflammation of the GI tract causing vomiting and diarrhea.",
        "remedies": "Hypoallergenic diets and immunosuppressive medications prescribed by a vet.",
        "emergency": False
    },
    "Feline Obesity": {
        "description": "Excessive weight leading to increased risk of diabetes and joint issues.",
        "remedies": "Measured meal feeding, transition to canned food, and encouraging play/exercise.",
        "emergency": False
    },
    "Rabies (Cat)": {
        "description": "A fatal viral disease. All cats should be vaccinated.",
        "remedies": "No cure. Preventable only with vaccination. Fatal once symptoms show.",
        "emergency": True
    },
    "Feline Heartworm": {
        "description": "Parasitic infection of the heart and lungs. Prevention is key as treatment is limited.",
        "remedies": "Supportive care via vet (oxygen therapy, steroids). No safe adulticide treatment exists for cats.",
        "emergency": True
    }
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/symptoms", methods=["GET"])
def get_symptoms():
    """Return all known symptoms (for autocomplete)."""
    return jsonify({"symptoms": symptom_cols})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Expects JSON: { "pet_type": "dog"|"cat", "symptoms": ["vomiting", ...] }
    Returns top-3 predictions with confidence, description, remedies, and emergency flag.
    """
    data = request.get_json(force=True)
    pet_type = data.get("pet_type", "dog").lower()
    symptoms = [s.strip().lower().replace(" ", "_") for s in data.get("symptoms", [])]

    # Build feature vector
    feat = {}
    for fn in feature_names:
        if fn.startswith("pet_"):
            feat[fn] = 1 if fn == f"pet_{pet_type}" else 0
        else:
            feat[fn] = 1 if fn in symptoms else 0

    X = np.array([[feat[fn] for fn in feature_names]])

    # Predict probabilities
    probs = model.predict_proba(X)[0]
    top_indices = probs.argsort()[::-1][:3]

    results = []
    for idx in top_indices:
        disease = label_encoder.inverse_transform([idx])[0]
        confidence = round(float(probs[idx]) * 100, 1)
        
        info = DISEASE_INFO.get(disease, {})
        description = info.get("description", "Consult your veterinarian for more information.")
        remedies = info.get("remedies", "Consult your veterinarian.")
        emergency = info.get("emergency", False)

        results.append({
            "disease": disease,
            "confidence": confidence,
            "description": description,
            "remedies": remedies,
            "emergency": emergency
        })

    return jsonify({"predictions": results})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
