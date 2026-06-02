"""
Amini Platform · Database Seeder
Run once after the database is created:  python3 seed.py
"""

import json, hashlib, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_tables, SessionLocal, User, Vouch, Message, VouchRequest, Pipeline, ProfileView

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── SEED DATA (mirrors store.js SEED) ─────────────────────────────────────────

USERS = [
    { "id":"admin-1",  "email":"admin@amini.africa",       "password":"admin123", "role":"admin",     "name":"Amini Admin",                  "avatar":"AA" },
    { "id":"cand-1",   "email":"solomon@amini.africa",     "password":"demo123",  "role":"candidate", "name":"Solomon Kinyua",
      "title":"COO · Operations & Scale-up", "location":"Nairobi, Kenya",
      "bio":"Operations leader with 10+ years scaling businesses across East Africa. Built from zero: $22M+ GMV, 175K+ customers, 4 markets.",
      "markets":["KE","NG","GH"], "work_visas":["KE","NG"],
      "skills":["Operations","Strategy","Team Building","Cross-border Expansion","P&L Management"],
      "ubuntu_score":82, "subscription":"career_accelerator", "billing_cycle":"yearly",
      "avatar":"SK", "identity_verified":True, "vouch_ids":["v1","v2","v3"],
      "joined":"2026-01-15", "profile_views":247 },
    { "id":"cand-2",   "email":"amara@amini.africa",       "password":"demo123",  "role":"candidate", "name":"Amara Mensah",
      "title":"Senior Product Manager · Fintech", "location":"Accra, Ghana",
      "bio":"PM with 7 years in mobile money and B2B SaaS. Led 3 product launches generating $8M+ in new revenue.",
      "markets":["GH","NG"], "work_visas":["GH"],
      "skills":["Product Strategy","Roadmapping","Agile","Data Analysis","User Research"],
      "ubuntu_score":71, "subscription":"pro", "billing_cycle":"monthly",
      "avatar":"AM", "identity_verified":False, "vouch_ids":["v4"],
      "joined":"2026-02-10", "profile_views":134 },
    { "id":"cand-3",   "email":"fatima@amini.africa",      "password":"demo123",  "role":"candidate", "name":"Fatima Diallo",
      "title":"Software Engineer · Backend", "location":"Lagos, Nigeria",
      "bio":"Backend engineer with expertise in Node.js, Go, and distributed systems. Built payment infrastructure processing $50M/month.",
      "markets":["NG","GH"], "skills":["Node.js","Go","PostgreSQL","Microservices","AWS"],
      "ubuntu_score":64, "subscription":"free", "avatar":"FD",
      "identity_verified":False, "vouch_ids":[], "joined":"2026-03-05", "profile_views":89 },
    { "id":"hr-1",     "email":"talent@techcorp.africa",   "password":"demo123",  "role":"hr",        "name":"Ngozi Okafor",
      "company":"TechCorp Africa", "company_size":"201-500", "title":"Head of Talent Acquisition",
      "markets":["NG","KE","GH"], "subscription":"growth", "billing_cycle":"monthly",
      "avatar":"NO", "joined":"2026-01-20", "lookups_used":87, "lookups_limit":150 },
    { "id":"hr-2",     "email":"recruit@panaf.com",        "password":"demo123",  "role":"hr",        "name":"Kwame Asante-Boateng",
      "company":"PanAf Talent Group", "company_size":"11-50", "title":"Senior Recruitment Consultant",
      "markets":["GH","KE"], "subscription":"starter", "avatar":"KB",
      "joined":"2026-02-05", "lookups_used":14, "lookups_limit":20 },
]

VOUCHES = [
    { "id":"v1", "candidate_id":"cand-1", "witness_name":"Wilson A",
      "witness_role":"Head of Global Expansion · Yango", "witness_initials":"WA", "witness_color":"#1A5FA8",
      "context":"manager", "status":"verified", "weight":9.2, "duration":52, "media_url":"demo",
      "quote":"Solomon built our entire operations from nothing. I've never seen someone move faster without breaking things. I'd hire him again tomorrow.",
      "created_at":"2026-03-10" },
    { "id":"v2", "candidate_id":"cand-1", "witness_name":"Ebe Alma",
      "witness_role":"VP Engineering · Moove Africa", "witness_initials":"EA", "witness_color":"#C1440E",
      "context":"peer", "status":"verified", "weight":8.7, "duration":47, "media_url":"demo",
      "quote":"Working with Solomon is rare. He translates strategy into execution without losing the detail. Never once played blame-games when things broke.",
      "created_at":"2026-03-15" },
    { "id":"v3", "candidate_id":"cand-1", "witness_name":"James Kariuki",
      "witness_role":"CEO · Sendy Africa", "witness_initials":"JK", "witness_color":"#065F46",
      "context":"client", "status":"verified", "weight":9.5, "duration":58, "media_url":"demo",
      "quote":"Solomon doesn't need hand-holding. He asked the right questions upfront, then disappeared into execution mode. Exceptional operator.",
      "created_at":"2026-04-01" },
    { "id":"v4", "candidate_id":"cand-2", "witness_name":"Ama Asante",
      "witness_role":"CTO · Zeepay", "witness_initials":"AA", "witness_color":"#7C3AED",
      "context":"manager", "status":"verified", "weight":8.1, "duration":41, "media_url":"demo",
      "quote":"Amara shipped our core payments product in 6 weeks flat. Exceptional product sense and customer empathy.",
      "created_at":"2026-04-05" },
    { "id":"v5", "candidate_id":"cand-1", "witness_name":"Fatima Nkosi",
      "witness_role":"CFO · Copia Global", "witness_initials":"FN", "witness_color":"#0F6E56",
      "context":"peer", "status":"pending", "weight":0, "duration":44, "media_url":"demo",
      "quote":None, "created_at":"2026-05-20" },
]

MESSAGES = [
    { "id":"m1", "from_id":"hr-1", "from_name":"Ngozi Okafor", "from_company":"TechCorp Africa",
      "to_witness":"Wilson A", "about_candidate_id":"cand-1", "about_candidate_name":"Solomon Kinyua",
      "body":"Hi Chisom, I'm reviewing Solomon Kinyua for a COO role. Could you tell me more about how he handled cross-border expansion at Yango?",
      "reply":"Happy to connect! Solomon was exceptional — built our East Africa ops in under 4 months, hired 3 country leads. Thursday after 3pm EAT works great.",
      "status":"replied", "created_at":"2026-05-22", "replied_at":"2026-05-22" },
    { "id":"m2", "from_id":"hr-2", "from_name":"Kwame Asante-Boateng", "from_company":"PanAf Talent",
      "to_witness":"Ama Asante", "about_candidate_id":"cand-2", "about_candidate_name":"Amara Mensah",
      "body":"Hi Ama, I came across Amara Mensah's Amini profile. I'm hiring for a Head of Product role — how did Amara handle stakeholder management under pressure?",
      "reply":None, "status":"sent", "created_at":"2026-05-24", "replied_at":None },
]

VOUCH_REQUESTS = [
    { "id":"vr1", "candidate_id":"cand-3", "witness_email":"manager@startup.ng",
      "witness_name":"Bode Adeyemi", "status":"sent", "created_at":"2026-05-23" },
]

PIPELINE = [
    { "id":"pl1", "hr_id":"hr-1", "candidate_id":"cand-1", "stage":"Shortlisted", "added_at":"2026-05-20" },
    { "id":"pl2", "hr_id":"hr-1", "candidate_id":"cand-2", "stage":"Reviewing",   "added_at":"2026-05-22" },
]

PROFILE_VIEWS = [
    { "id":"pv1", "candidate_id":"cand-1", "hr_id":"hr-1", "hr_name":"Ngozi Okafor",        "hr_initials":"NO", "hr_color":"#1A5FA8", "hr_company":"TechCorp Africa",   "hr_title":"Head of Talent Acquisition",       "viewed_at":"2026-05-25T14:32:00", "read":False },
    { "id":"pv2", "candidate_id":"cand-1", "hr_id":"hr-2", "hr_name":"Kwame Asante-Boateng","hr_initials":"KB", "hr_color":"#065F46", "hr_company":"PanAf Talent Group", "hr_title":"Senior Recruitment Consultant",     "viewed_at":"2026-05-24T09:15:00", "read":False },
    { "id":"pv3", "candidate_id":"cand-1", "hr_id":"hr-1", "hr_name":"Ngozi Okafor",        "hr_initials":"NO", "hr_color":"#1A5FA8", "hr_company":"TechCorp Africa",   "hr_title":"Head of Talent Acquisition",       "viewed_at":"2026-05-22T16:45:00", "read":True  },
    { "id":"pv4", "candidate_id":"cand-1", "hr_id":"hr-2", "hr_name":"Kwame Asante-Boateng","hr_initials":"KB", "hr_color":"#065F46", "hr_company":"PanAf Talent Group", "hr_title":"Senior Recruitment Consultant",     "viewed_at":"2026-05-21T11:20:00", "read":True  },
    { "id":"pv5", "candidate_id":"cand-2", "hr_id":"hr-2", "hr_name":"Kwame Asante-Boateng","hr_initials":"KB", "hr_color":"#065F46", "hr_company":"PanAf Talent Group", "hr_title":"Senior Recruitment Consultant",     "viewed_at":"2026-05-18T08:05:00", "read":True  },
    { "id":"pv6", "candidate_id":"cand-2", "hr_id":"hr-1", "hr_name":"Ngozi Okafor",        "hr_initials":"NO", "hr_color":"#1A5FA8", "hr_company":"TechCorp Africa",   "hr_title":"Head of Talent Acquisition",       "viewed_at":"2026-05-23T13:00:00", "read":False },
]


def seed():
    create_tables()
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("⚠  Database already seeded — skipping. Run with --force to re-seed.")
            return

        for u in USERS:
            row = User(
                id=u["id"], email=u["email"], password=hash_pw(u["password"]),
                role=u["role"], name=u.get("name",""), title=u.get("title",""),
                location=u.get("location",""), bio=u.get("bio",""),
                avatar=u.get("avatar","??"),
                identity_verified=u.get("identity_verified", False),
                subscription=u.get("subscription","free"),
                billing_cycle=u.get("billing_cycle"),
                ubuntu_score=u.get("ubuntu_score",0),
                profile_views_count=u.get("profile_views",0),
                joined=u.get("joined"),
                markets=json.dumps(u.get("markets",[])),
                skills=json.dumps(u.get("skills",[])),
                work_visas=json.dumps(u.get("work_visas",[])),
                other_markets=json.dumps(u.get("other_markets",[])),
                vouch_ids=json.dumps(u.get("vouch_ids",[])),
                company=u.get("company",""), company_size=u.get("company_size",""),
                company_location=u.get("company_location",""),
                lookups_used=u.get("lookups_used",0),
                lookups_limit=u.get("lookups_limit",20),
            )
            db.add(row)

        for v in VOUCHES:
            db.add(Vouch(**v))

        for m in MESSAGES:
            db.add(Message(**m))

        for r in VOUCH_REQUESTS:
            db.add(VouchRequest(**r))

        for p in PIPELINE:
            db.add(Pipeline(**p))

        for pv in PROFILE_VIEWS:
            db.add(ProfileView(**pv))

        db.commit()
        print(f"✓ Seeded {db.query(User).count()} users  |  "
              f"{db.query(Vouch).count()} vouches  |  "
              f"{db.query(Message).count()} messages  |  "
              f"{db.query(Pipeline).count()} pipeline entries")
    finally:
        db.close()


if __name__ == "__main__":
    force = "--force" in sys.argv
    if force:
        from app import Base, engine
        Base.metadata.drop_all(bind=engine)
        print("⚡ Tables dropped — re-seeding…")
    seed()
