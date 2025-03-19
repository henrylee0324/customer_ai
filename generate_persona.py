import random

def generate_age():
    """
    生成年齡：使用高斯分布 (平均33歲、標準差10)
    並將年齡限制在 18 到 65 歲之間（主要為成年人）。
    """
    age = int(random.gauss(33, 10))
    return max(18, min(age, 65))

def generate_gender():
    """
    性別：越南人口男女比例接近均衡。
    """
    return random.choice(["Male", "Female"])

def generate_marital_status(age):
    """
    婚姻狀況：根據年齡進行區分
      - 年輕人（<30歲）：較大機率為單身（約70%）
      - 中年人（30-50歲）：大部分為已婚（約80%）
      - 年長者（50歲以上）：大部分為已婚（85%），少數可能為離婚或喪偶（15%）
    """
    if age < 30:
        return random.choices(["Single", "Married"], weights=[0.7, 0.3])[0]
    elif age < 50:
        return random.choices(["Single", "Married"], weights=[0.2, 0.8])[0]
    else:
        return random.choices(["Married", "Widowed/Divorced"], weights=[0.85, 0.15])[0]

def generate_education():
    """
    教育程度：根據越南現況，大部分受過高中教育，
    少部分擁有大學或更高學歷。
      - High School: 約60%
      - College: 約30%
      - Graduate: 約10%
    """
    return random.choices(["High School", "College", "Graduate"], weights=[0.6, 0.3, 0.1])[0]

def generate_income():
    """
    收入水平：大部分客戶為低至中等收入，
    少部分為高收入。
      - Low: 70%
      - Medium: 25%
      - High: 5%
    """
    return random.choices(["Low", "Medium", "High"], weights=[0.7, 0.25, 0.05])[0]

def generate_job_type():
    """
    職業類型：參考越南主要就業結構，
    包括農業、服務業、小商販、上班族、專業人士等。
      - Agriculture/Farming: 30%
      - Service/Small Business: 30%
      - Office Worker/Clerical: 20%
      - Professional/Teacher/Engineer: 10%
      - Self-employed/Entrepreneur: 10%
    """
    job_types = [
        "Agriculture/Farming",
        "Service/Small Business",
        "Office Worker/Clerical",
        "Professional/Teacher/Engineer",
        "Self-employed/Entrepreneur"
    ]
    weights = [0.3, 0.3, 0.2, 0.1, 0.1]
    return random.choices(job_types, weights=weights)[0]

def generate_life_insurance_coverage():
    """
    商業壽險覆蓋率較低：大約 11% 的客戶可能已有壽險。
    """
    return random.random() < 0.11

def generate_insurance_interest(marital_status, age):
    """
    保險需求興趣：根據婚姻狀況及年齡，
    設定可能關注的保險產品。
      - 健康保險/重大疾病險普遍受關注
      - 已婚者特別關注壽險/儲蓄險與子女教育險
      - 年輕客戶可能對意外險感興趣
      - 年長者可能考慮退休金產品
    """
    interests = []
    # 健康險普及
    interests.append("Health Insurance/Critical Illness")
    
    if marital_status == "Married":
        interests.append("Life Insurance/Savings")
        if age >= 30:
            interests.append("Child Education")
        if age >= 50:
            interests.append("Retirement Pension")
    
    # 年輕族群有較高意外險需求
    if age < 40:
        interests.append("Accident Insurance")
    
    # 過濾重複項目
    return list(set(interests))

def generate_family_structure(marital_status):
    """
    家庭結構：已婚者通常家庭規模較大（3~5人），
    單身者則可能只有1~3人（與父母同住或單獨居住）。
    """
    if marital_status == "Married":
        family_size = random.choice([3, 4, 5])
    else:
        family_size = random.choice([1, 2, 3])
    return {"family_size": family_size}

def generate_risk_attitude():
    """
    對風險態度：越南大多數客戶傾向保守，
    分布大約為：
      - Risk-Averse: 80%
      - Moderate: 15%
      - Risk-Seeking: 5%
    """
    return random.choices(["Risk-Averse", "Moderate", "Risk-Seeking"], weights=[0.8, 0.15, 0.05])[0]

def generate_preferred_channel():
    """
    購買渠道偏好：目前大部分客戶仍偏好線下銷售，
    少數年輕人可能傾向線上交流。
      - Offline: 80%
      - Online: 20%
    """
    return random.choices(["Offline", "Online"], weights=[0.8, 0.2])[0]

def generate_sales_acceptance():
    """
    對推銷方式的接受度：
      - High Acceptance (較樂於接受銷售): 60%
      - Medium Acceptance: 30%
      - Low Acceptance (抗拒較強): 10%
    """
    return random.choices(["High Acceptance", "Medium Acceptance", "Low Acceptance"], weights=[0.6, 0.3, 0.1])[0]

def generate_mbti():
    """
    MBTI 性格類型根據全球統計數據生成：
      ISTJ: 11.6%
      ISFJ: 13.8%
      INFJ: 1.5%
      INTJ: 2.1%
      ISTP: 5.4%
      ISFP: 8.8%
      INFP: 4.4%
      INTP: 3.3%
      ESTP: 4.3%
      ESFP: 8.5%
      ENFP: 8.1%
      ENTP: 2.7%
      ESTJ: 8.7%
      ESFJ: 12.3%
      ENFJ: 2.5%
      ENTJ: 1.8%
    """
    mbti_types = [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]
    weights = [
        11.6, 13.8, 1.5, 2.1,
        5.4, 8.8, 4.4, 3.3,
        4.3, 8.5, 8.1, 2.7,
        8.7, 12.3, 2.5, 1.8
    ]
    return random.choices(mbti_types, weights=weights)[0]

def simulate_customer():
    """
    根據越南社會各項現實數據與 MBTI 性格設計，
    生成一個模擬客戶的完整資料。
    """
    age = generate_age()
    gender = generate_gender()
    marital_status = generate_marital_status(age)
    education = generate_education()
    income = generate_income()
    job_type = generate_job_type()
    has_life_insurance = generate_life_insurance_coverage()
    insurance_interest = generate_insurance_interest(marital_status, age)
    family_structure = generate_family_structure(marital_status)
    risk_attitude = generate_risk_attitude()
    preferred_channel = generate_preferred_channel()
    sales_acceptance = generate_sales_acceptance()
    mbti = generate_mbti()

    customer = {
        "age": age,
        "gender": gender,
        "marital_status": marital_status,
        "education": education,
        "income": income,
        "job_type": job_type,
        "has_life_insurance": has_life_insurance,
        "insurance_interest": insurance_interest,
        "family_structure": family_structure,
        "risk_attitude": risk_attitude,
        "preferred_channel": preferred_channel,
        "sales_acceptance": sales_acceptance,
        "mbti": mbti
    }
    return customer

# 測試：生成 10 個模擬客戶並印出
if __name__ == "__main__":
    for i in range(10):
        cust = simulate_customer()
        print(f"Customer {i+1}:")
        print(cust)
        print("-" * 40)