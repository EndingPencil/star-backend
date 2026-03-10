from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from skyfield.api import load, Star
from skyfield.data import hipparcos

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL MEMORY (The "Static" Data) ---
print("⏳ Loading Hipparcos star catalog... (This might take a minute the first time)")
with load.open(hipparcos.URL) as f:
    df = hipparcos.load_dataframe(f)

# FILTER 1: Keep only stars visible to the naked eye (Magnitude <= 6.0)
df_visible = df[df['magnitude'] <= 6.0]

# FILTER 2: Filter out stars with missing coordinate data (NaN values) to prevent JSON crashes
df_visible = df_visible[df_visible['ra_degrees'].notnull()]

print(f"✅ Loaded {len(df_visible)} visible stars.")

# --- THE API ENDPOINT ---
@app.get("/visible-stars")
def get_visible_stars():
    stars_data = []
    
    for hip_id, row in df_visible.iterrows():
        stars_data.append({
            "id": int(hip_id),      
            # Force conversion from Numpy floats to standard Python floats
            "ra": float(row.ra_degrees),   
            "dec": float(row.dec_degrees), 
            "mag": float(row.magnitude)    
        })
        
    return {"count": len(stars_data), "stars": stars_data}