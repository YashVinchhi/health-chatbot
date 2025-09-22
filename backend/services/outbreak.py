def check_area(pincode):
    """Check for disease outbreaks in an area"""
    # Dummy implementation - replace with actual data
    outbreaks = {
        "110001": ["Dengue", "Malaria"],
        "400001": ["COVID-19"],
        "600001": ["H1N1"]
    }
    return outbreaks.get(pincode, [])