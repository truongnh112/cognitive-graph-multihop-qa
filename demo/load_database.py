#Gọi redis, tạo database client
#Nếu trong thư mục chưa notebook đã có file dump.rdb thì gọi lệnh này nó sẽ tự restore database
#import redis_server
import redis
#db.ping()
def load_db():
    db = redis.StrictRedis(host = 'localhost', port=6379)
    return db
db = load_db()
print(db.ping())