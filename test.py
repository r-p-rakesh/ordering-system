from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

stored_hash = "$2b$12$WDpcW2/1k7GbDTUKoagO8ujIa6sQFrV.1FQp03.8RmiacK2O/KfFi"
test_password = "testpass123"

result = pwd_context.verify(test_password, stored_hash)
print("Match result:", result)