from sqlalchemy.orm import Session
from app.models.word import Word


SAMPLE_WORDS = [
    # (word_en, word_vn, pronunciation, word_type, example_en, example_vn, level, topic)
    ("cat",          "con mèo",          "/kæt/",           "noun", "The cat is sleeping on the sofa.",         "Con mèo đang ngủ trên ghế sofa.",         "A1", "animals"),
    ("dog",          "con chó",          "/dɔːɡ/",          "noun", "The dog is barking at the door.",          "Con chó đang sủa ở cửa.",                 "A1", "animals"),
    ("bird",         "con chim",         "/bɜːrd/",         "noun", "A beautiful bird is singing outside.",     "Một con chim đẹp đang hót bên ngoài.",    "A1", "animals"),
    ("elephant",     "con voi",          "/ˈelɪfənt/",      "noun", "The elephant is very large and strong.",  "Con voi rất to và mạnh.",                 "A1", "animals"),
    ("tiger",        "con hổ",           "/ˈtaɪɡər/",       "noun", "The tiger is the largest wild cat.",      "Con hổ là loài mèo hoang lớn nhất.",      "A2", "animals"),

    ("apple",        "quả táo",          "/ˈæpəl/",         "noun", "I eat an apple every morning.",           "Tôi ăn một quả táo mỗi sáng.",            "A1", "food"),
    ("banana",       "quả chuối",        "/bəˈnænə/",       "noun", "The banana is yellow and sweet.",         "Quả chuối màu vàng và ngọt.",             "A1", "food"),
    ("rice",         "cơm / gạo",        "/raɪs/",          "noun", "We eat rice every day.",                  "Chúng tôi ăn cơm mỗi ngày.",              "A1", "food"),
    ("pizza",        "bánh pizza",       "/ˈpiːtsə/",       "noun", "We ordered a large pizza for dinner.",    "Chúng tôi đặt một chiếc pizza lớn.",      "A1", "food"),
    ("coffee",       "cà phê",           "/ˈkɒfi/",         "noun", "I drink coffee every morning.",           "Tôi uống cà phê mỗi sáng.",               "A1", "food"),

    ("book",         "quyển sách",       "/bʊk/",           "noun", "I am reading an interesting book.",       "Tôi đang đọc một cuốn sách hay.",         "A1", "education"),
    ("school",       "trường học",       "/skuːl/",         "noun", "She goes to school by bus.",              "Cô ấy đến trường bằng xe buýt.",          "A1", "education"),
    ("teacher",      "giáo viên",        "/ˈtiːtʃər/",      "noun", "My teacher is very kind.",                "Giáo viên của tôi rất tốt bụng.",         "A1", "education"),
    ("student",      "học sinh / sinh viên", "/ˈstjuːdənt/","noun", "The student is studying for the exam.",   "Học sinh đang ôn thi.",                   "A1", "education"),
    ("library",      "thư viện",         "/ˈlaɪbreri/",     "noun", "I study at the library every evening.",   "Tôi học ở thư viện mỗi tối.",             "A2", "education"),

    ("car",          "xe ô tô",          "/kɑːr/",          "noun", "My father drives a red car to work.",     "Bố tôi lái xe ô tô đỏ đi làm.",          "A1", "transport"),
    ("bus",          "xe buýt",          "/bʌs/",           "noun", "The school bus arrives at 7 AM.",         "Xe buýt trường đến lúc 7 giờ sáng.",      "A1", "transport"),
    ("bicycle",      "xe đạp",           "/ˈbaɪsɪkəl/",     "noun", "I ride my bicycle to school every day.", "Tôi đạp xe đến trường mỗi ngày.",         "A1", "transport"),
    ("airplane",     "máy bay",          "/ˈerˌpleɪn/",     "noun", "The airplane is flying high in the sky.","Máy bay đang bay cao trên bầu trời.",      "A2", "transport"),
    ("train",        "tàu hỏa",          "/treɪn/",         "noun", "We traveled by train last weekend.",      "Chúng tôi đi tàu hỏa cuối tuần trước.",   "A2", "transport"),

    ("house",        "ngôi nhà",         "/haʊs/",          "noun", "They live in a big house.",               "Họ sống trong một ngôi nhà to.",           "A1", "home"),
    ("bedroom",      "phòng ngủ",        "/ˈbedrʊm/",       "noun", "My bedroom is on the second floor.",      "Phòng ngủ của tôi ở tầng hai.",           "A1", "home"),
    ("kitchen",      "nhà bếp",          "/ˈkɪtʃɪn/",       "noun", "She is cooking in the kitchen.",          "Cô ấy đang nấu ăn trong bếp.",            "A1", "home"),
    ("garden",       "khu vườn",         "/ˈɡɑːrdən/",      "noun", "We have flowers in our garden.",          "Chúng tôi có hoa trong vườn.",            "A2", "home"),
    ("furniture",    "đồ nội thất",      "/ˈfɜːrnɪtʃər/",   "noun", "The furniture in this room is modern.",   "Đồ nội thất trong phòng này rất hiện đại.","B1", "home"),

    ("happy",        "vui vẻ / hạnh phúc","/ˈhæpi/",        "adj",  "She is very happy today.",               "Cô ấy rất vui hôm nay.",                  "A1", "feelings"),
    ("sad",          "buồn",             "/sæd/",           "adj",  "He felt sad after the bad news.",         "Anh ấy buồn sau khi nghe tin xấu.",       "A1", "feelings"),
    ("angry",        "tức giận",         "/ˈæŋɡri/",        "adj",  "She was angry because of the mistake.",   "Cô ấy tức giận vì lỗi lầm đó.",           "A2", "feelings"),
    ("excited",      "hào hứng / phấn khích","/ɪkˈsaɪtɪd/","adj",  "The children are excited about the trip.","Lũ trẻ hào hứng về chuyến đi.",           "A2", "feelings"),
    ("nervous",      "lo lắng / hồi hộp","/ˈnɜːrvəs/",     "adj",  "I feel nervous before the exam.",         "Tôi cảm thấy hồi hộp trước kỳ thi.",      "B1", "feelings"),

    ("run",          "chạy",             "/rʌn/",           "verb", "He runs 5km every morning.",              "Anh ấy chạy 5km mỗi sáng.",               "A1", "actions"),
    ("eat",          "ăn",               "/iːt/",           "verb", "We eat dinner at 7 PM.",                  "Chúng tôi ăn tối lúc 7 giờ.",             "A1", "actions"),
    ("sleep",        "ngủ",              "/sliːp/",         "verb", "Children need to sleep 8 hours a day.",   "Trẻ em cần ngủ 8 tiếng mỗi ngày.",        "A1", "actions"),
    ("study",        "học",              "/ˈstʌdi/",        "verb", "She studies English every evening.",      "Cô ấy học tiếng Anh mỗi buổi tối.",       "A1", "actions"),
    ("travel",       "du lịch / đi lại", "/ˈtrævəl/",       "verb", "They love to travel around the world.",   "Họ thích du lịch vòng quanh thế giới.",   "A2", "actions"),

    ("beautiful",    "đẹp",              "/ˈbjuːtɪfəl/",    "adj",  "The sunset is so beautiful.",             "Hoàng hôn thật đẹp.",                     "A2", "description"),
    ("important",    "quan trọng",       "/ɪmˈpɔːrtənt/",   "adj",  "Health is very important.",               "Sức khỏe rất quan trọng.",                "A2", "description"),
    ("difficult",    "khó",              "/ˈdɪfɪkəlt/",     "adj",  "This exam is very difficult.",            "Bài thi này rất khó.",                    "A2", "description"),
    ("quickly",      "nhanh chóng",      "/ˈkwɪkli/",       "adv",  "She finished her work quickly.",          "Cô ấy hoàn thành công việc nhanh chóng.", "B1", "description"),
    ("carefully",    "cẩn thận",         "/ˈkerffəli/",     "adv",  "Please drive carefully.",                 "Vui lòng lái xe cẩn thận.",               "B1", "description"),
]


def seed_words(db: Session):
    count_new = 0
    for row in SAMPLE_WORDS:
        word_en, word_vn, pronunciation, word_type, example_en, example_vn, level, topic = row
        exists = db.query(Word).filter(Word.word_en == word_en.lower()).first()
        if not exists:
            db.add(Word(
                word_en=word_en.lower(),
                word_vn=word_vn,
                pronunciation=pronunciation,
                word_type=word_type,
                example_en=example_en,
                example_vn=example_vn,
                level=level,
                topic=topic,
            ))
            count_new += 1

    db.commit()
    print(f"✅ Seed hoàn tất — thêm {count_new} từ mới ({len(SAMPLE_WORDS)} từ trong bộ mẫu)")