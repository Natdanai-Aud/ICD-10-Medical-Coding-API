export type CaseLineRole =
  | "principal"
  | "comorbidity"
  | "complication"
  | "external_cause"
  | "procedure"
  | "other";

export interface GuidelineCaseLine {
  role: CaseLineRole;
  diagnosisText: string;
  code: string | null;
  codeStatus: "resolved" | "unresolved" | "unknown";
}

export interface GuidelineCaseExample {
  exampleNo: string;
  page?: number;
  scenarioTh: string;
  lines: GuidelineCaseLine[
  {
    "exampleNo": "1-0",
    "page": 7,
    "scenarioTh": "ผู้ป่วยเป็นโรคเบาหวานชนิดที่ 2 ความดันโลหิตสูง และโคเลสเตอรอสสูง รับการรักษาต่อเนื่องมาตลอด ครั้งนี้มีอาการปวดศีรษะ มาก แพทย์ตรวจพบความดันโลหิต 200/140 mmHg Filadeh malignant hypertension รับไว้รักษาในโรงพยาบาล ลณา ไทย Malignant hypertension",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.7 example 1-0"
  },
  {
    "exampleNo": "1-1",
    "page": 33,
    "scenarioTh": "ผู้ป่วยมีไข้สูงและหนาวสั่นมา 1 วัน ตรวจพบอุณหภูมิ 39°C หายใจ 26 ครั้ง/นาที ชีพจร 100 ครั้ง/นาที ความดันโลหิต 120/70 ม.ม. ปรอท กดเจ็บที่ costovertebral angle ข้างขวา ตรวจบัสสาวะพบเม็ดเลือดขาวจํานวนมาก เพาะเชื้อในปัสสาวะและในเลือดขึ้น ป E. coli แพทย์วินิจฉัยว่า ล๐น66 pyelonephritis due to E. coli และ sepsis due to E. 00// 1 oie eaten",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "Acute tubulo-interstitial nephritis",
        "code": "N10",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.33 example 1-1"
  },
  {
    "exampleNo": "1-2",
    "page": 32,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.32 example 1-2 (not parsed)"
  },
  {
    "exampleNo": "1-3",
    "page": 84,
    "scenarioTh": "ผู้ป่วยหญิงอายุ 30 ปี มาด้วยมีประจําเดือนออกมากในแต่ละครั้งตามรอบประจําเดือนปถติ มีอาการอ่อนเพลีย ลุกขึ้นหน้ามืด ตรวจ ร่างกายพบว่าซีด ตรวจทางห้องปฏิบัติการพบว่า haemoglobin 6.0 g % , MCV 70 fl, blood smear มีลักษณะ hypochromic microcytic แพทย์วินิจฉัยว่า \"๓6ก๐เท่าธฎ ล และ chronic posthaemorthagic anaemia พ92.0 Excessive and frequent menstruation with regular cycle",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "Excessive and frequent menstruation with regular cycle",
        "code": "N92.0",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.84 example 1-3"
  },
  {
    "exampleNo": "1-4",
    "page": 95,
    "scenarioTh": "ผู้ป่วยหญิงอายุ 50 ปี มาด้วยมีใช้สูงมา 1 วัน มีอาการคลื่นไส้ อาเจียน ท้องเดิน เหนื่อยหอบ ตรวจร่างกายพบชีพจร 140 ครั้ง/ นาที ไม่สม่าเสมอ ความดันโลหิต 140/90 ม.ม.ปรอท อยู่ในลักษณะ restless waz agitation ประวัติอดีตเป็น hyperthyroidism ก: (Graves disease) มา 2 ปี ได้รับการรักษามา 6 เดือน",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.95 example 1-4"
  },
  {
    "exampleNo": "1-5",
    "page": 132,
    "scenarioTh": "หญิงอายุ 70 ปี เมื่อ 3 เดือนก่อนมาโรงพยาบาลความจําเสียไป ลืมง่าย คิดคํานวณผิดๆ ถูกๆ บางครั้งไม่สามารถตัดสินใจในปัญหา ง่ายๆ ได้ ตรวจ CT scan พบ multiple areas of infarction ที่บริเวณ cerebral cortex ทั้งสองข้าง แพทย์วินิจฉัยว่า เทนไม่-ทกลแต1 ป dementia ก่อนมาโรงพยาบาล 1 วันแขนขาซ้ายอ่อนแรง มี facial weakness upper motor neuron Way aphasia ตรวจ CT scan WU เหโลตณ์เอท เพิ่มขึ้นและมี thrombosis ของ middle cerebral ลพอ วินิจฉัยว่า ischaemic stroke cerebral artery",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "* Middle cerebral artery syndrame",
        "code": "G46.0",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.132 example 1-5"
  },
  {
    "exampleNo": "1-6",
    "page": 37,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.37 example 1-6 (not parsed)"
  },
  {
    "exampleNo": "1-7",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 1-7 (missing/not found by OCR)"
  },
  {
    "exampleNo": "1-8",
    "page": 181,
    "scenarioTh": "ผู้ป่วยปวดหูขวา ช่องหูบวม แพทย์ตรวจพบ hyphae สีขาวในช่องหูที่อักเสบ วินิจฉัยว่า ๐ย์น5 externa from aspergillus 2 แพทย์สรปจําหนน่วย : 0ฝ7ฝ77ว7จ+++++'@ฒซ%ให้งหัส 2 '' 844.81 Other forms of asperioss ก การวินิจฉ่ม ----วววว (1622 0แร๑เทอทร in mycoses",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.181 example 1-8"
  },
  {
    "exampleNo": "1-9",
    "page": 114,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.114 example 1-9 (not parsed)"
  },
  {
    "exampleNo": "1-10",
    "page": 48,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.48 example 1-10 (not parsed)"
  },
  {
    "exampleNo": "1-11",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 1-11 (missing/not found by OCR)"
  },
  {
    "exampleNo": "1-12",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 1-12 (missing/not found by OCR)"
  },
  {
    "exampleNo": "1-13",
    "page": 275,
    "scenarioTh": "ผู้ป่วยชาย อายุ 50 ปี แพทย์วินิจฉัยว่า avascular necrosis of hip นัดทําผ่าตัด total hip arthroplasty จากประวัติพบว่ามี osteoarthritis of hip ข้างเดียวจากการใช้ยาสเตียรอยด์ ผู้ให้รหัสปรึกษาแพทย์ขอให้เปลี่ยนการวินิจฉัยหลักเป็น unilateral secondary osteoarthritis of hip ให้การวินิจฉัยร่วมว่า osteoporosis และระบุสาเหตุภายนอกว่าเกิดจากการใช้ยาสเตียรอยด์",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.275 example 1-13"
  },
  {
    "exampleNo": "1-14",
    "page": 292,
    "scenarioTh": "ผู้ป่วยชาย อายุ 35 ปี มาด้วยบวมมานาน 1 ปี ตรวจปัสสาวะพบ red blood cells 10 เซลล์/HPF, protein 2+ ตรวจเลือดพบ BUN 10 มิลลิกรัม/เดซิลิตร creatinine 1.0 มิลลิกรัม/เดซิลิตร แพทย์วินิจฉัยว่า chronic nephritic syndrome ทํา kidney biopsy ผลเป็น diffuse mesangial proliferative glomerulonephritis ตรวจ immunofluorescence พบ IgA deposit",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.292 example 1-14"
  },
  {
    "exampleNo": "1-15",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 1-15 (missing/not found by OCR)"
  },
  {
    "exampleNo": "1-16",
    "page": 339,
    "scenarioTh": "ผู้ป่วยหญิงอายุ 25 ปี แพทย์วินิจฉัยว่า clear cell carcinoma of vagina เนื่องจากมารดาของผู้ป่วยเคยได้รับยา diethyl stilbestrol (DES) ระหว่างตั้งครรภ์ผู้ป่วย",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.339 example 1-16 (not parsed)"
  },
  {
    "exampleNo": "1-17",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 1-17 (missing/not found by OCR)"
  },
  {
    "exampleNo": "1-18",
    "page": 348,
    "scenarioTh": "ผู้ป่วยหญิงอายุ 20 ปี มาด้วยอาการใจสั่น ตรวจร่างกายพบว่าชีพจร 110 ครั้ง/นาที EKG พบ sinus tachycardia ทํา echocardiogram ปกติ ตรวจ thyroid function ปกติ",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.348 example 1-18 (not parsed)"
  },
  {
    "exampleNo": "1-19",
    "page": 376,
    "scenarioTh": "ผู้ป่วยขับรถเก๋งชนต้นไม้ ได้รับบาดเจ็บหลายแห่ง มีภาวะหมดสติชั่วคราว (concussion) หูขาด แผลฉีกที่แก้มและต้นขา ฟกช้ำที่ใบหน้า คอ และไหล่",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "$02.4- ที่ไม่มีการฉีกขาดของเหงือกในตําแหน่งที่ไม่มีฟัน (edentulous) ซึ่ง",
        "code": "S02.6",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.376 example 1-19"
  },
  {
    "exampleNo": "1-20",
    "page": 395,
    "scenarioTh": "หญิงอายุ 70 ปี ลื่นหกล้มขณะทํางานบ้าน สะโพกกระแทกพื้น ปวดจนเดินไม่ได้ ถ่ายภาพรังสีพบ closed fracture of neck of femur, undisplaced intracapsular fracture",
    "lines": [
      {
        "role": "external_cause",
        "diagnosisText": "สาเหตุภายนอก ลื่นหกล้มขณะทํางานบ้าน Fall อท same level from slipping, tripping and stumbling at",
        "code": "W01.03",
        "codeStatus": "unresolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.395 example 1-20"
  },
  {
    "exampleNo": "1-21",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 1-21 (missing/not found by OCR)"
  },
  {
    "exampleNo": "1-22",
    "page": 450,
    "scenarioTh": "ผู้ป่วย end stage renal disease ได้รับการฟอกเลือดล้างไต มาด้วยอาการไข้ แพทย์วินิจฉัยว่า infected vascular dialysis catheter จากเชื้อ Staphylococcus aureus ซึ่งตื้อยา methicillin",
    "lines": [
      {
        "role": "comorbidity",
        "diagnosisText": "การวินิจฉัยร่วม End stage renal disease End stage เอทล disease",
        "code": "N18.5",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.450 example 1-22"
  },
  {
    "exampleNo": "2-0",
    "page": 7,
    "scenarioTh": "ผู้ปวยปวดท้องทันทีทันใต แพทย์ห้องฉุกเฉินวินิจฉัยว่า ๑๐น19 abdomen รับไว้รักษาในโรงพยาบาล แพทย์ที่หอผู้ป่วยวินิจฉัยว่า peritonitis ศัลยแพทย์ผ่าตัดเปิดช่องท้องพบ perforated chronic duodenal ulcer ทําผ่าตัด simple suture with omental graft Perforated chronic duodenal uicer ตัวอย่างที่ 3 0 ผู้ป่วยมาด้วยอาการไข้ ไอ หอบ แพทย์รับไว้ในโรงพยาบาล วินิจฉัยว่า 5๐01000008| pneumonia of right uper lobe An 3 วันต่อมา มีไข้สูง หนาวสั้น ความดันโลหิตตั๋า แพทย์วินิจฉัยว่ามี ๑๐01๐ 5ก๐๕เป็นโรคแทรก ข้ายเข้ารักษาใน cu อีก 7 วันต่อมาจึงย้ายกลับ หอผู้ป่วย รักษาต่ออีก 2 วันจึงกลับบ้านได้ Streptococcal pneumonia of right upper lobe",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.7 example 2-0"
  },
  {
    "exampleNo": "2-1",
    "page": 33,
    "scenarioTh": "ผู้ป่วย alcoholic cirrhosis of liver, Child class C มาด้วยมีไข้และหนาวสั่นมา 1 วัน ตรวจร่างกายพบ palmar erythema, spider nevi และ ascites อุณหภูมิ 38.5°C ชีพจร 110 ครั้ง/นาที ตรวจทางห้องปฏิบัติการพบเม็ดเลือดขาว 15,000 เซลล์/ม.ม.3 เกล็ดเลือด 100,000 ตัว/ม.ม.3 serum creatinine 1.5 มิลลิกรัม/ด.ล. เจาะน้ําในช่องท้องตรวจไม่พบเซลล์ ตรวจไม่พบแหล่งติดเชื้อที่อื่น แพทย์วินิจฉัยว่า sepsis ให้ยาปฏิชีวนะ ceftriaxone ทางหลอดเลือดดํา ไข้ลงใน 4 วัน จึงเปลี่ยนยาปฏิชีวนะ จําหน่ายกลับบ้าน ผลเพาะเชื้อในเลือดไม่ขึ้น",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.33 example 2-1"
  },
  {
    "exampleNo": "2-2",
    "page": 67,
    "scenarioTh": "แพทย์รับไว้ในโรงพยาบาลเรื่องชัก ตรวจ CT scan สมองพบก้อนขนาด 3 ซ.ม. ตรวจภาพรังสีทรวงอกพบ lung เทลรร ขนาด 4 ซ.ม. บริเวณ left upper lobe ทํา open brain biopsy ผลพยาธิวิทยาเป็น metastatic adenocarcinoma ทํา bronchoscopic biopsy ผล พยาธิวิทยาเป็น adenocarcinoma แพทย์วินิจฉัยว่าเป็นมะเร็งทุติยภูมิที่สมอง กระจายมาจากมะเร็งปอด จําหน่ายกลับบ้านโดย ไม่ได้ให้เคมีบําบัดหรือรังสีรักษา เพราะผู้ป่วยอายุมาก",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.67 example 2-2"
  },
  {
    "exampleNo": "2-3",
    "page": 84,
    "scenarioTh": "ผู้ป่วยชายอายุ 50 ปี อาเจียนเป็นเลือดมา 1 วัน ตรวจร่างกายพบว่าชีต ตรวจทางห้องปฏิบัติการพบ haemoglobin 7.8 ๆ % ทํา gastroscopy WU acute haemorrhagic gastritis แพทย์ให้ packed red blood cell 1 ซูนิต วินิจฉัยว่า ลอนเอ haemorrhagic gastritis ป ร่วมกับ ล0บ1๑ posthaemorrhagic anaemia ก",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "Malignant neoplasm of descending colon",
        "code": "C18.14",
        "codeStatus": "unresolved"
      },
      {
        "role": "complication",
        "diagnosisText": ". โรคแทรก Intraoperative haemorrhage Haemorrhage and haematoma complicating a procedure, not",
        "code": "T81.0",
        "codeStatus": "resolved"
      },
      {
        "role": "complication",
        "diagnosisText": "Acute posthaemorthagic anaemia Acute posthaemorrhagic anaemia",
        "code": "D62",
        "codeStatus": "resolved"
      },
      {
        "role": "external_cause",
        "diagnosisText": "Unintentional cut, puncture, perforation or haemorrhage during ล",
        "code": "Y60.0",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.84 example 2-3"
  },
  {
    "exampleNo": "2-4",
    "page": 95,
    "scenarioTh": "ผู้ป่วยชายอายุ 25 ปี มาด้วยแขนขาอ่อนแรงมา 30 นาที ตรวจร่างกายพบ generalized muscle weakness โดยเฉพาะอย่างยิ่ง บริเวณ proximal muscle ต่อมไทรอยด์โต 40 กรัม ชีพจร 120 ครั้ง/นาที ตรวจพบ exophthalmos ตรวจทางห้องปฏิบัติการ พบระดับ serum potassium 2.0 มิลลิโมล/ลิตร ติดตามอาการใน 2 ชั่วโมงต่อมาพบว่าอาการกล้ามเนื้ออ่อนแรงหายไป ระดับ serum potassium กลับมาปกติ แพทย์วินิจฉัยว่า 6หลสงธร disease waz thyrotoxic hypokalaemia with periodic paralysis",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.95 example 2-4"
  },
  {
    "exampleNo": "2-5",
    "page": 132,
    "scenarioTh": "หญิงอายุ 65 ปี ได้รับการวินิจฉัยว่า 'ทน|ย“เกรณะ! dementia มานาน 1 ปี เมื่อ 2 สัปดาห์ก่อนมาโรงพยาบาลมีอาการหวาดระแวง คิด ว่าคนอื่นปลอมตัวมาเป็นลูกสาว แพทย์รับไว้ในโรงพยาบาลเพื่อควบคุมอาการ Aedes muiti-infarct dementia | การวินิจฉัยหลัก [กวิฉังม | 1 007ว7นวงฬ|",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.132 example 2-5"
  },
  {
    "exampleNo": "2-6",
    "page": 37,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.37 example 2-6 (not parsed)"
  },
  {
    "exampleNo": "2-7",
    "page": 179,
    "scenarioTh": "แพทย์วินิจฉัยว่าผู้ป่วยเป็น senile hypermature cataract ตาขวา แลสะ senile combined cataract ตาซ้าย วัดระดับสายตาได้ VA right eye = hand movement with pinhole not improve; VA left eye = 1/60 or 20/1200 with pinhole not improve ทําผ่าตัดตาข้างขวาเพียงตาเดียว ! ู020แพทย์ธุปจทหน่ย ฏฏ111โวง ฮู7ฝฆยให้ทั้ล งภภไไไ",
    "lines": [
      {
        "role": "other",
        "diagnosisText": "oo ended re HEEL OE coger Waka 22) FE OEE",
        "code": "S28",
        "codeStatus": "resolved"
      },
      {
        "role": "principal",
        "diagnosisText": "ง ภารวินิจฉัยหลัก Senile hypermature cataract Senile hypermature cataract",
        "code": "H25.2",
        "codeStatus": "resolved"
      },
      {
        "role": "comorbidity",
        "diagnosisText": "การวินิจฉัยร่วม Blindness, monocular",
        "code": "H54.4",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.179 example 2-7"
  },
  {
    "exampleNo": "2-8",
    "page": 182,
    "scenarioTh": "ผู้ป่วยปวดหู มีไข้สูง ช่องหูบวมมาก มีประวัติเป็นโรคเบาหวานชนิดที่ 2 รับประทานยาไม่สม่าเสมอ แพทย์วินิจฉัยว่า กาลกอก1 Otitis externa อ ย ก",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.114 example 2-8 (not parsed)"
  },
  {
    "exampleNo": "2-9",
    "page": 114,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.114 example 2-9 (not parsed)"
  },
  {
    "exampleNo": "2-10",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 2-10 (missing/not found by OCR)"
  },
  {
    "exampleNo": "2-11",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 2-11 (missing/not found by OCR)"
  },
  {
    "exampleNo": "2-12",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 2-12 (missing/not found by OCR)"
  },
  {
    "exampleNo": "2-13",
    "page": 277,
    "scenarioTh": "ผู้ป่วยหญิง any 50 ปี มาด้วยอาการปวดเข่าบริเวณรอบลูกสะบ้า ปวดเวลาจะลุกหรือจะนั่งคุกเข่า แพทย์ตรวจพบว่ามีเสียงเหมือน ขัดกระดาษทราย (crepitus) ที่ลูกสะบ้าขณะเคลื่อนไหว จินิจฉัยว่า ลก1อท่อ\" เทอธ pain syndrome ผู้ให้รหัสปรึกษาแพทย์ขอให้เปลี่ยน",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.277 example 2-13"
  },
  {
    "exampleNo": "2-14",
    "page": 293,
    "scenarioTh": "ผู้ป่วยหญิงอายุ 30 ปี มาด้วยไข้ หนาวสั่น ตรวจร่างกายพบอุณหภูมิ 39 °C ตรวจไม่พบ costovertebral tenderness ตรวจทาง ป ห้องปฏิบัติการพบ Hb 12 กรัม % เม็ดเลือดขาว 16,000 เซลล์/ม.ม.53 neutrophil 90 % lymphocyte 10 % ตรวจปัสสาวะพบเม็ด ก เลือดขาว 15 เซลล์/966 เพาะเชื้อในปัสสาวะขึ้น 6. ๐๐/ 105 ๐0อกป/มิสลิลิตร ผล กอก00นแอ ขึ้น 6. coll",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.293 example 2-14"
  },
  {
    "exampleNo": "2-15",
    "page": 56,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.56 example 2-15 (not parsed)"
  },
  {
    "exampleNo": "2-16",
    "page": 339,
    "scenarioTh": "ทารกเดี่ยว คลอดครบกําหนดในโรงพยาบาล แพทย์วินิจฉัยว่ามีภาวะ hypoglycaemia",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.339 example 2-16 (not parsed)"
  },
  {
    "exampleNo": "2-17",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 2-17 (missing/not found by OCR)"
  },
  {
    "exampleNo": "2-18",
    "page": 348,
    "scenarioTh": "ผู้ป่วยหญิงอายุ 20 ปี มาด้วยอาการใจสั้น ตรวจรางกายพบวาชพจร 110 ครง/นาท ต่อมไทรอยด์โต 35 กรม ม tremor และ lid tag ตรวจทางห้องปฏิบัติการพบว่าระดับไทรอยด์ฮอร์โมนสูง ระดับ TSH ตํา EKG พบ sinus tachycardia ก : : ฝฝ8๐09๐9๐0รง3ง+ก แลเลลล 1ยบยฒ Hyperthyroidism with diffuse goitre E05.0 Hyperthyroidism with diffuse goitre กจินฉัรม 0ไกภง ไปไป1ชี ป BRADYCARDIA: 800.1 sinus bradycardia ได้ เช่น เกิดจาก hypothyroidism หรือเกิดจาก ยาโรคหัวใจ ให้วินิจฉัยภาวะที่เป็นสาเหตุ โดยไม่ต้องวินิจฉัยว่ามี อ an ๆ A A เกณฑ์การวันจฉย sinus bradycardia 2 aw. เลง coast tw vio Bradycardia หมายถึงภาวะที่หัวใจเต้นน้อยกว่าหรือเท่ากับ เกณฑ์การให้รหัส 60 ครั้งต่อนาที โดยไม่สามารถระบุชนิดของภาวะนีได้ หรือระบุได้ว่า เป็น sinus bradycardia แต่ไม่สามารถระบุสาเหตุได้ ถ้าแพทย์วินิจฉัยว่า ๒๒ลส๐ลส่ ล หรือ sinus bradycardia หากแพทย์สามารถระบุชนิดของ bradycardia ได้ ให้วินิจฉัย ให้รหัส ฟิ00.1 Bradycardia, unspecified และถ้าแพทย์วินิจฉัย s ว 1 . . จ toe vow = J",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "Hyperthyroidism with diffuse goitre Hyperthyroidism with diffuse goitre",
        "code": "E05.0",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.348 example 2-18"
  },
  {
    "exampleNo": "2-19",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 2-19 (missing/not found by OCR)"
  },
  {
    "exampleNo": "2-20",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 2-20 (missing/not found by OCR)"
  },
  {
    "exampleNo": "2-21",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 2-21 (missing/not found by OCR)"
  },
  {
    "exampleNo": "2-22",
    "page": 450,
    "scenarioTh": "ผู้ป่วยวัณโรคปอด ตรวจพบ AFB จากเสมหะ ได้รับยาต้านวัณโรคมา 2 เดือน ไม่ตอบสนองการรักษา เพาะเชื้อพบว่าตื้อยาต้านวัณโรค INH และ ethambutol",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.450 example 2-22"
  },
  {
    "exampleNo": "3-0",
    "page": 7,
    "scenarioTh": "ผู้ป่วยมาด้วยอาการไข้ ไอ หอบ แพทย์รับไว้ในโรงพยาบาล วินิจฉัยว่า 5๒01000008 pneumonia of right uper lobe อีก 3 วันต่อมา",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.7 example 3-0 (not parsed)"
  },
  {
    "exampleNo": "3-1",
    "page": 33,
    "scenarioTh": "ผู้ป่วยมาด้วยไข้และปวดหลังด้านขวา 1 วัน ตรวจร่างกายพบว่ากดเจ็บที่หลังด้านขวา ตรวจทางห้องปฏิบัติการพบฮีโมโกลบิน 12 กรัม % เม็ดเลือดขาว 12,000 เซลล์/ม.ม.3 เกล็ดเลือด 60,000 ตัว/ม.ม.3 sodium 140 มิลลิโมล/ลิตร potassium 50 มิลลิโมล /ลิตร chloride 100 มิลลิโมล/ลิตร carbon dioxide 12 มิลลิโมล/ลิตร ตรวจปัสสาวะพบเม็ดเลือดขาวจํานวนมาก เพาะเชื้อปัสสาวะขึ้นเชื้อ 5. ๐ เพาะเชื้อในเลือดไม่ขึ้น ให้ยาปฏิชีวนะ ไข้ลง กลับบ้านได้ใน 7 วัน แพทย์วินิจฉัย ล0น16 pyelonephritis due to ซิ. coli ร่วมกับ severe sepsis - ;",
    "lines": [
      {
        "role": "comorbidity",
        "diagnosisText": "การวินิจฉัยร่วม Severe sepsis Systemic inflammatory response syndrome of infectious origin",
        "code": "R65.1",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.33 example 3-1"
  },
  {
    "exampleNo": "3-2",
    "page": 67,
    "scenarioTh": "ผู้ปวยมาด้วยอาการหน้าและแขนบวม แพทย์วินิจฉัยว่าเป็น superior vena cava obstruction รับไว้ในโรงพยาบาล ทํา CT scan ทรวงอกพบ mediastinal mass และ right lower lung mass ขนาด 3 ซ.ม. ทํา bronchoscopic biopsy ผลชิ้นเนื้อเป็น small cell carcinoma แพทย์วินิจฉัยว่า รน๒ธท่อ' vena cava obstruction จาก mediastinal metastasis ของมะเร็งปอด รักษาโดยฉายแสงชนิด supervoltage",
    "lines": [
      {
        "role": "procedure",
        "diagnosisText": "Radiotherapy Radiotherapy session",
        "code": "Z51.0",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.67 example 3-2"
  },
  {
    "exampleNo": "3-3",
    "page": 87,
    "scenarioTh": "ผู้ป่วยชายอายุ 40 ปี เป็น deep vein thrombosis both lower legs ได้รับยา warfarin มา 3 เดือน เมื่อ 1วันก่อนมาโรงพยาบาลมี ) อาการปวดศีรษะรุนแรง ชีมลง ตรวจ CT brain พบ intracerebral haemorrhage at frontal lobe ซักประวัติได้ความว่าผู้ป่วย รับประทานยา warfarin ผิดขนาดด้วยเข้าใจผิด จากวันละ 2 เม็ดเป็นวันละ 4 เม็ด PT-INR 10.0 แพทย์ให้ FFP, vit « ง ทําผ่าตัด craniotomy เพื่อ remove clot : - ย",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "ทางใตพบ glomerulonephritis ตรวจพบโปรตีนและเม็ด",
        "code": "D69.0",
        "codeStatus": "resolved"
      },
      {
        "role": "other",
        "diagnosisText": "ทางใตพบ glomerulonephritis ตรวจพบโปรตีนและเม็ด",
        "code": "D69.2",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.87 example 3-3"
  },
  {
    "exampleNo": "3-4",
    "page": 97,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.97 example 3-4 (not parsed)"
  },
  {
    "exampleNo": "3-5",
    "page": 133,
    "scenarioTh": "หญิงอายุ 75 ปี แพทย์รับไว้ในโรงพยาบาลด้วยเรื่องไข้ ปวดหลัง ตรวจร่างกายพบไข้ 39°C กดเจ็บบริเวณสีข้างด้านขวา ตรวจ",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.133 example 3-5 (not parsed)"
  },
  {
    "exampleNo": "3-6",
    "page": 91,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.91 example 3-6 (not parsed)"
  },
  {
    "exampleNo": "3-7",
    "page": 180,
    "scenarioTh": "แพทย์วินิจฉัยว่าผู้ป่วยเป็น senile hypermature cataract ตาขวา และ senile combined cataract ตาซ้าย วัดระดับสายตาได้ VA right eye = hand movement with pinhole not improve; VA left eye = 1/60 or 20/1200 with pinhole not improve ทําผ่าตัดทั้งสองตา Blindness H54.0 Blindness, binocular",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "Blindness Blindness, binocular",
        "code": "H54.0",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.180 example 3-7"
  },
  {
    "exampleNo": "3-8",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 3-8 (missing/not found by OCR)"
  },
  {
    "exampleNo": "3-9",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 3-9 (missing/not found by OCR)"
  },
  {
    "exampleNo": "3-10",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 3-10 (missing/not found by OCR)"
  },
  {
    "exampleNo": "3-11",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 3-11 (missing/not found by OCR)"
  },
  {
    "exampleNo": "3-12",
    "page": 46,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.46 example 3-12 (not parsed)"
  },
  {
    "exampleNo": "3-13",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 3-13 (missing/not found by OCR)"
  },
  {
    "exampleNo": "3-14",
    "page": 294,
    "scenarioTh": "ผู้ป่วยมาด้วยไข้ หนาวสั้น และกดเจ็บบริเวณ costovertebral tendemess ข้างขวา ทํา ultrasound wu hydroureter การวินิจฉัยหลัก | กรินิจฉัวม ไกพจะ 0000 0 1ไ170 20 0 8ษณ--- | DRUG2AND HEAVY-METAL-INDUCED + ยาลตความดันโลหิต เช่น ยาในกลุ่ม angiotensin TUBULO-INTERSTITIACLAND TUBULAR converting enzyme (ACE) inhibitor, angiotensin CONDITIONS:3N14 receptor blockage (ARB) = Lithium carbonate ทําให้เกิด nephrogenic diabetes เกณฑ์การวินิจฉัย insipidus และ tubulo-interstitial disease",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.294 example 3-14"
  },
  {
    "exampleNo": "3-15",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 3-15 (missing/not found by OCR)"
  },
  {
    "exampleNo": "3-16",
    "page": 340,
    "scenarioTh": "ทารกเดี่ยว คลอดครบกําหนดในโรงพยาบาล ก. แพทย์วินิจฉัยว่า ๒๒5๒11๒810ๆ/ distress syndrome ต่อมามี pneumothorax ส่งไป รับการรักษาต่อที่โรงพยาบาล ข. โรงพยาบาล ก. สรุปการวินิจฉัยและให้รหัสดังนี้ 522.0 Respiratory distress syndrome of newbom | กรวินิจัร์ม |-2 77๊ไไไป|ป 238.0 Singleton, born in hospital",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "Pneumothorax originating in the perinatal period",
        "code": "P25.1",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.340 example 3-16"
  },
  {
    "exampleNo": "3-17",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 3-17 (missing/not found by OCR)"
  },
  {
    "exampleNo": "3-18",
    "page": 349,
    "scenarioTh": "ผู้ปวยหญิงอายุ 50 ปี เป็นโรคความดันโลหิตสูง ได้รับยา ล!๒ก๐0 และ อแย่ละ๐ ตรวจพบว่าชีพจร 40 ครั้ง/นาที แพทย์รับไว้ใน โรงพยาบาล ตรวจ EKG พบ sinus bradycardia แพทย์สงสัยว่าอาจเกิดจากยาลดความตันโลหิต จึงให้หยุดยา ล1อก010! uaz ditiazem ให้ยาลตความต้นโลหิตตัวอื่นแทน หลังจากนั้น 3 วัน 6 กลับมาเป็น normal sinus rhythm ป เทรม",
    "lines": [
      {
        "role": "principal",
        "diagnosisText": "AND OTHER CARDIAC SOUNDS:¥ valvular heart disease, cardiac shunt",
        "code": "R01",
        "codeStatus": "resolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.349 example 3-18"
  },
  {
    "exampleNo": "3-19",
    "page": null,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 example 3-19 (missing/not found by OCR)"
  },
  {
    "exampleNo": "3-20",
    "page": 397,
    "scenarioTh": "คนงานหญิงอายุ 45 ปี ขณะทํางานในโรงงาน หม้อน้้าระเบิด น้้าร้อนกระเด็นลวกบริเวณลําตัวเป็นแผลลอกแดงทั้งตัว แพทย์ วินิจฉัยว่า ฝ่าไหส่ degree burn 25% of body surface area ๆ พ35.62 Explosion and rupture of boiler, in industrial and construction area, while working for income",
    "lines": [
      {
        "role": "external_cause",
        "diagnosisText": "อุบัติเหตุหม้อน้้าระเบิดขณะทํางานในโรงงาน Explosion and rupture of boiler, in industrial and",
        "code": "W35.62",
        "codeStatus": "unresolved"
      }
    ],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.397 example 3-20"
  },
  {
    "exampleNo": "3-21",
    "page": 422,
    "scenarioTh": "",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.422 example 3-21 (not parsed)"
  },
  {
    "exampleNo": "3-22",
    "page": 450,
    "scenarioTh": "ผู้ป่วยมาด้วยไข้ หนาวสั่น ปวดชายโครงขวา ตรวจปัสสาวะพบเม็ดเลือดขาวจํานวนมาก เพาะเชื้อจากปัสสาวะขึ้น Escherichia coli ชนิด extended spectrum beta-lactamase (ESBL) resistance แพทย์วินิจฉัยว่า acute pyelonephritis จาก E. coli ชนิด ESBL resistance",
    "lines": [],
    "needsReview": true,
    "sourceRef": "Guideline 2017 p.450 example 3-22"
  }
];
