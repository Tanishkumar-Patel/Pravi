from datetime import date

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def evaluate_eligibility(scheme, family, member=None):
    rules = scheme.eligibility_criteria or {}
    reasons = []
    
    # 1. Family Income Check (Applies to both Family and Member schemes)
    if 'max_family_income' in rules:
        if float(family.annual_income) > float(rules['max_family_income']):
            reasons.append(f"Family income ₹{family.annual_income} exceeds maximum threshold of ₹{rules['max_family_income']}")

    # 2. Member-level checks (Only if scheme targets individuals)
    if scheme.beneficiary_type == 'MEMBER':
        if not member:
            return {"eligible": False, "reasons": ["Member details are required for this scheme."]}
        
        age = calculate_age(member.date_of_birth)
        
        if 'min_age' in rules and age < rules['min_age']:
            reasons.append(f"Member age ({age}) is below minimum required age ({rules['min_age']})")
            
        if 'max_age' in rules and age > rules['max_age']:
            reasons.append(f"Member age ({age}) exceeds maximum allowed age ({rules['max_age']})")

        if 'gender' in rules and rules['gender'].upper() != 'ANY':
            if member.gender.upper() != rules['gender'].upper():
                reasons.append(f"Scheme is restricted to {rules['gender']} applicants")

        if 'education' in rules and rules['education']:
            if (member.education or '').lower() != rules['education'].lower():
                reasons.append(f"Requires education level: {rules['education']}")

    return {
        "eligible": len(reasons) == 0,
        "reasons": reasons
    }