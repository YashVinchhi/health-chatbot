def get_schedule(age):
    """Get vaccination schedule for given age"""
    # Dummy implementation - replace with actual schedule
    schedules = {
        0: ["BCG", "OPV-0", "Hepatitis B-1"],
        6: ["DPT-1", "OPV-1", "Hepatitis B-2"],
        10: ["DPT-2", "OPV-2"],
        14: ["DPT-3", "OPV-3", "Hepatitis B-3"],
        36: ["MMR"],
        60: ["DPT Booster", "OPV Booster"]
    }
    return schedules.get(age, [])