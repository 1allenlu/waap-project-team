# MongoDB Demo Guide for TAs

This guide shows exactly what to demonstrate when TAs ask to see MongoDB running.

---

## 🎯 What TAs Will Check

1. **Code Review**: Verify your code uses MongoDB (not in-memory storage)
2. **Live Demo**: Show MongoDB shell with your database running

---

## ✅ Part 1: Code Using MongoDB

### Files to Show TAs:

#### 1. `data/db_connect.py` - MongoDB Connection
```python
# Line 27-28: Connection string
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

# Lines 368-370: MongoClient usage
client_candidate = pm.MongoClient(
    os.environ.get("MONGO_URI", "mongodb://localhost:27017"),
    serverSelectionTimeoutMS=2000)
```

#### 2. `cities/queries.py` - Using MongoDB Operations
```python
# Line 5: Import MongoDB connection
import data.db_connect as dbc

# Line 44: Create operation uses MongoDB
new_id = dbc.create(CITY_COLLECTION, flds)

# Line 96: Read operation uses MongoDB
return dbc.read(CITY_COLLECTION)

# Line 82: Delete operation uses MongoDB
ret = dbc.delete(CITY_COLLECTION, {NAME: name, STATE_CODE: state_code})
```

#### 3. `common.mk` - Local MongoDB Enabled
```makefile
# Line 5: Using local MongoDB (not cloud)
export CLOUD_MONGO = 0
```

---

## ✅ Part 2: MongoDB Shell Demo

### Step-by-Step Demo Script

Open your terminal and follow these commands:

### 1. Check MongoDB is Running

```bash
brew services list | grep mongodb
```

**Expected output:**
```
mongodb-community started ✓
```

If not started:
```bash
brew services start mongodb-community
```

---

### 2. Open MongoDB Shell

```bash
mongosh
```

**You'll see:**
```
Current Mongosh Log ID: ...
Connecting to: mongodb://127.0.0.1:27017
Using MongoDB: 8.2.1
Using Mongosh: 2.x.x

test>
```

---

### 3. Essential Commands to Show TAs

Copy and paste these commands one by one:

```javascript
// 1. Show all databases
show dbs

// 2. Switch to your project database
use geo2025DB

// 3. Show all collections (tables)
show collections

// 4. Count documents in cities collection
db.cities.countDocuments()

// 5. Show all cities (or first few)
db.cities.find()

// 6. Show cities with pretty formatting
db.cities.find().pretty()

// 7. Show just one city
db.cities.findOne()

// 8. Insert a new city (demonstration)
db.cities.insertOne({
  name: "Sample City",
  state_code: "SC"
})

// 9. Find the city you just inserted
db.cities.findOne({ name: "Sample City" })

// 10. Count again to show it increased
db.cities.countDocuments()

// 11. Delete the test city
db.cities.deleteOne({ name: "Sample City" })

// 12. Verify deletion
db.cities.countDocuments()

// 13. Exit the shell
exit
```

---

### 4. Advanced Commands (If TAs Ask)

```javascript
// Show database stats
db.stats()

// Show collection stats
db.cities.stats()

// Find cities in a specific state
db.cities.find({ state_code: "NY" })

// Count cities by state
db.cities.aggregate([
  { $group: { _id: "$state_code", count: { $sum: 1 } } }
])

// Show indexes
db.cities.getIndexes()
```

---

## 🚀 Quick Demo Flow (30 seconds)

If TAs are in a hurry, show this:

```bash
# 1. Open shell
mongosh

# 2. Switch to database
use geo2025DB

# 3. Show data exists
db.cities.find()

# 4. Show count
db.cities.countDocuments()

# 5. Exit
exit
```

---

## 🔧 Add Sample Data Before Demo

Run this Python script to ensure you have data to show:

```bash
python -c "
import sys
sys.path.insert(0, '.')
import cities.queries as cqry

# Add sample cities if database is empty
if cqry.num_cities() < 3:
    cqry.create({'name': 'New York', 'state_code': 'NY'})
    cqry.create({'name': 'Los Angeles', 'state_code': 'CA'})
    cqry.create({'name': 'Chicago', 'state_code': 'IL'})

print(f'Database has {cqry.num_cities()} cities ready for demo!')
"
```

---

## 🎬 Complete Demo Script

Here's what to say to the TAs:

### Opening Statement:
> "Let me show you that our application is using MongoDB locally."

### Demo:
```bash
# Terminal 1: Show MongoDB is running
brew services list | grep mongodb

# Terminal 2: Open MongoDB shell
mongosh

# In mongosh:
use geo2025DB
show collections
db.cities.find().pretty()
db.cities.countDocuments()

# Point out to TAs:
# - Database name: geo2025DB
# - Collection: cities
# - Documents have: name, state_code, _id
# - _id is MongoDB ObjectId (auto-generated)

exit
```

### Closing Statement:
> "As you can see, the data is stored in MongoDB, not in memory. The code in `data/db_connect.py` uses PyMongo to connect to `mongodb://localhost:27017`."

---

## 📋 Troubleshooting

### If MongoDB isn't running:
```bash
brew services start mongodb-community
# Wait 2-3 seconds
brew services list | grep mongodb
```

### If database is empty:
```bash
# Run your Flask app to populate data
python server/endpoints.py

# Or add data manually via mongosh:
mongosh geo2025DB --eval "db.cities.insertOne({name: 'Test', state_code: 'TS'})"
```

### If mongosh command not found:
```bash
brew install mongosh
```

---

## ✅ Checklist Before Meeting TAs

- [ ] MongoDB is running (`brew services list`)
- [ ] Database has some data (`mongosh geo2025DB` → `db.cities.find()`)
- [ ] You can open mongosh without errors
- [ ] You know the database name: `geo2025DB`
- [ ] You know the collection names: `cities`, `states`
- [ ] Code shows PyMongo imports and usage

---

## 🎓 Key Points to Emphasize

1. **Not using in-memory storage** - Data persists after server restarts
2. **Using PyMongo** - Python MongoDB driver (see `import pymongo as pm`)
3. **Local MongoDB** - Running on `localhost:27017` (not cloud)
4. **CLOUD_MONGO=0** - Environment variable confirms local usage
5. **Collections** - Cities and states are stored in MongoDB collections

---

## 📚 Additional Resources

- MongoDB Shell Docs: https://docs.mongodb.com/mongodb-shell/
- PyMongo Docs: https://pymongo.readthedocs.io/

---

**Good luck with your demo! 🚀**
