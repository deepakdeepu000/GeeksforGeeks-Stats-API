# 🚀 GeeksforGeeks Profile Scraper API

A comprehensive REST API to fetch user profile statistics, coding scores, and solved problems from GeeksforGeeks profiles.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright)](https://playwright.dev/)

## 📑 Table of Contents

- [Base URL](#base-url)
- [Endpoints](#endpoints)
- [Request Examples](#request-examples)
- [Response Schemas](#response-schemas)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)
- [Code Examples](#code-examples)

---

## 🌐 Base URL

```
Production: https://your-app.onrender.com
Local: http://localhost:8000
```

---

## 📍 Endpoints

### 1. Root Endpoint

**GET** `/`

Returns API information and available endpoints.

**Response:**
```json
{
  "message": "GFG Scraper API is running",
  "version": "1.0.0",
  "endpoints": {
    "profile": "/{userName}/profile",
    "stats": "/{userName}/stats",
    "problems": "/{userName}/problems",
    "card": "/{userName}/card"
  },
  "docs": "/docs"
}
```

---

### 2. Get User Profile

**GET** `/profile/{userName}/`

Retrieves comprehensive profile information including coding score, rank, streaks, and statistics.

**Parameters:**
- `userName` (path, required): GeeksforGeeks username

**Example Request:**
```bash
GET /profile/[username]
```

**Example Response:**
```json
{
  "userName": "gfg_user_",
  "fullName": "GFG USer",
  "designation": "Software Engineer",
  "codingScore": 1250,
  "problemsSolved": 245,
  "instituteRank": 12,
  "articlesPublished": 5,
  "potdStreak": 15,
  "longestStreak": 42,
  "potdsSolved": 87
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `userName` | string | GeeksforGeeks username |
| `fullName` | string | User's full name |
| `designation` | string | User's designation/title |
| `codingScore` | integer | Total coding score |
| `problemsSolved` | integer | Total problems solved |
| `instituteRank` | integer | Rank in institution (0 if N/A) |
| `articlesPublished` | integer | Number of articles published |
| `potdStreak` | integer | Current POTD streak |
| `longestStreak` | integer | Longest POTD streak achieved |
| `potdsSolved` | integer | Total POTDs solved |

---

### 3. Get Problem Statistics

**GET** `/stats/{userName}`

Retrieves problem-solving statistics broken down by difficulty level.

**Parameters:**
- `userName` (path, required): GeeksforGeeks username
- `format` (query, optional): Response format - `json` (default) or `svg`

**Example Request (JSON):**
```bash
GET /stats/[username]/?format=json
```

**Example Response (JSON):**
```json
{
  "userName": "pampana__deepak",
  "School": 25,
  "Basic": 40,
  "Easy": 75,
  "Medium": 80,
  "Hard": 25,
  "totalProblemsSolved": 245
}
```

**Example Request (SVG):**
```bash
GET /stats/[username]/?format=svg
```

**Example Response (SVG):**
Returns an SVG image that can be embedded in markdown or HTML.

**Response Schema (JSON):**
| Field | Type | Description |
|-------|------|-------------|
| `userName` | string | GeeksforGeeks username |
| `School` | integer | School difficulty problems solved |
| `Basic` | integer | Basic difficulty problems solved |
| `Easy` | integer | Easy difficulty problems solved |
| `Medium` | integer | Medium difficulty problems solved |
| `Hard` | integer | Hard difficulty problems solved |
| `totalProblemsSolved` | integer | Sum of all problems solved |

---

### 4. Get Solved Problems List

**GET** `/problems/{userName}`

Retrieves a detailed list of ALL solved problems with titles and direct links.

**Parameters:**
- `userName` (path, required): GeeksforGeeks username

**Example Request:**
```bash
GET /problems/[username]
```

**Example Response:**
```json
{
  "userName": "gfg_user_",
  "problemsByDifficulty": {
    "School": 25,
    "Basic": 40,
    "Easy": 75,
    "Medium": 80,
    "Hard": 25
  },
  "Problems": {
    "School": [
      {
        "question": "Print 1 to n without using loops",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/print-1-to-n-without-using-loops/1"
      },
      {
        "question": "Sum of first n terms",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/sum-of-first-n-terms/1"
      }
    ],
    "Basic": [
      {
        "question": "LCM And GCD",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/lcm-and-gcd/1"
      }
    ],
    "Easy": [
      {
        "question": "Reverse Words in a String",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/reverse-words-in-a-given-string/1"
      }
    ],
    "Medium": [
      {
        "question": "Longest Substring Without Repeating Characters",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/longest-substring-without-repeating-characters/1"
      }
    ],
    "Hard": [
      {
        "question": "N-Queen Problem",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/n-queen-problem/1"
      }
    ]
  }
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `userName` | string | GeeksforGeeks username |
| `problemsByDifficulty` | object | Count of problems by difficulty |
| `Problems` | object | Nested object with arrays of problem details |
| `Problems.{difficulty}` | array | Array of problem objects |
| `Problems.{difficulty}[].question` | string | Problem title |
| `Problems.{difficulty}[].questionUrl` | string | Direct link to problem |

---

### 5. Get Stats Card (SVG Widget)

**GET** `/{userName}`

Direct endpoint for SVG stats card, useful for embedding in GitHub READMEs.

**Parameters:**
- `userName` (path, required): GeeksforGeeks username

**Example Request:**
```bash
GET /[username]
```

**Example Response:**
Returns an SVG image (Content-Type: `image/svg+xml`)

**Usage in Markdown:**
```markdown
![GFG Stats](https://gfg-stats-scraper.onrender.com/username)
```

**Usage in HTML:**
```html
<img src="https://gfg-stats-scraper.onrender.com/username" alt="GFG Stats" />
```

---

## ⚠️ Error Handling

All endpoints return errors in the following format:

### 404 Not Found
```json
{
  "detail": "User not found or private profile"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to fetch profile data"
}
```

### Common Error Responses

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `404` | User not found or profile is private |
| `500` | Server error (scraping failed) |
| `422` | Invalid input parameters |

---

## 🚦 Rate Limits

- **No authentication required**
- Requests are rate-limited by Render's infrastructure
- Recommended: Cache responses on your end
- SVG cards are cached for 4 hours (14400 seconds)

---

## 💻 Code Examples

### JavaScript/TypeScript

```javascript
// Fetch user profile
async function getUserProfile(username) {
  const response = await fetch(`https:/gfg-stats-scraper.onrender.com/${username}/profile`);
  
  if (!response.ok) {
    throw new Error('Profile not found');
  }
  
  const data = await response.json();
  console.log(data);
  return data;
}

// Fetch stats
async function getUserStats(username) {
  const response = await fetch(`https://gfg-stats-scraper.onrender.com/${username}/stats?format=json`);
  const data = await response.json();
  return data;
}

// Fetch all problems
async function getUserProblems(username) {
  const response = await fetch(`https://gfg-stats-scraper.onrender.com/${username}/problems`);
  const data = await response.json();
  return data;
}

// Usage
getUserProfile('gfg_user_')
  .then(profile => console.log('Profile:', profile))
  .catch(error => console.error('Error:', error));
```

### Python

```python
import requests

BASE_URL = "https://gfg-stats-scraper.onrender.com"

def get_user_profile(username):
    """Fetch user profile"""
    response = requests.get(f"{BASE_URL}/profile/{username}")
    response.raise_for_status()
    return response.json()

def get_user_stats(username, format="json"):
    """Fetch user statistics"""
    response = requests.get(f"{BASE_URL}/stats/{username}", params={"format": format})
    response.raise_for_status()
    
    if format == "svg":
        return response.text
    return response.json()

def get_user_problems(username):
    """Fetch all solved problems"""
    response = requests.get(f"{BASE_URL}/problems/{username}")
    response.raise_for_status()
    return response.json()

# Usage
try:
    profile = get_user_profile('gfg_user_')
    print(f"Coding Score: {profile['codingScore']}")
    print(f"Problems Solved: {profile['problemsSolved']}")
    
    stats = get_user_stats('gfg_user_')
    print(f"Medium problems: {stats['Medium']}")
    
except requests.exceptions.HTTPError as e:
    print(f"Error: {e}")
```

### cURL

```bash
# Get profile
curl -X GET "https://gfg-stats-scraper.onrender.com/profile/[username]"

# Get stats (JSON)
curl -X GET "https://gfg-stats-scraper.onrender.com/stats/[username]format=json"

# Get stats (SVG)
curl -X GET "https://gfg-stats-scraper.onrender.com/stats/[username]/format=svg" -o stats.svg

# Get problems
curl -X GET "https://gfg-stats-scraper.onrender.com/problems/[username]"

# Get SVG card
curl -X GET "https://gfg-stats-scraper.onrender.com/[username]" -o card.svg
```

### React/Next.js

```typescript
import { useState, useEffect } from 'react';

interface ProfileData {
  userName: string;
  fullName: string;
  codingScore: number;
  problemsSolved: number;
  instituteRank: number;
}

function GFGProfile({ username }: { username: string }) {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProfile() {
      try {
        const response = await fetch(
          `https://your-app.onrender.com/${username}/profile`
        );
        
        if (!response.ok) {
          throw new Error('Profile not found');
        }
        
        const data = await response.json();
        setProfile(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    }

    fetchProfile();
  }, [username]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!profile) return null;

  return (
    <div>
      <h1>{profile.fullName}</h1>
      <p>Coding Score: {profile.codingScore}</p>
      <p>Problems Solved: {profile.problemsSolved}</p>
      <img 
        src={`https://your-app.onrender.com/${username}/card`}
        alt="GFG Stats"
      />
    </div>
  );
}
```

---

## 📊 Full API Response Examples

### Complete Profile Response
```json
{
  "userName": "gfg_user_",
  "fullName": "John Doe",
  "designation": "Software Development Engineer",
  "codingScore": 2150,
  "problemsSolved": 387,
  "instituteRank": 5,
  "articlesPublished": 12,
  "potdStreak": 28,
  "longestStreak": 65,
  "potdsSolved": 142
}
```

### Complete Stats Response
```json
{
  "userName": "gfg_user_",
  "School": 45,
  "Basic": 62,
  "Easy": 120,
  "Medium": 135,
  "Hard": 25,
  "totalProblemsSolved": 387
}
```

### Complete Problems Response
```json
{
  "userName": "gfg_user_",
  "problemsByDifficulty": {
    "School": 45,
    "Basic": 62,
    "Easy": 120,
    "Medium": 135,
    "Hard": 25
  },
  "Problems": {
    "School": [
      {
        "question": "Array Subset of another array",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/array-subset-of-another-array/1"
      }
    ],
    "Basic": [
      {
        "question": "Remove duplicate elements from sorted Array",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/remove-duplicate-elements-from-sorted-array/1"
      }
    ],
    "Easy": [
      {
        "question": "Parenthesis Checker",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/parenthesis-checker/1"
      }
    ],
    "Medium": [
      {
        "question": "Binary Tree to DLL",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/binary-tree-to-dll/1"
      }
    ],
    "Hard": [
      {
        "question": "Matrix Chain Multiplication",
        "questionUrl": "https://practice.geeksforgeeks.org/problems/matrix-chain-multiplication/1"
      }
    ]
  }
}
```

---

## 🎨 Embed Stats Card

### In GitHub README

```markdown
# My GFG Profile

![GFG Stats](https://gfg-stats-scraper.onrender.com/your_username/card)

## Stats
- **Coding Score:** 2150
- **Problems Solved:** 387
```

### In HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Portfolio</title>
</head>
<body>
    <h1>My GeeksforGeeks Progress</h1>
    <img src="https://gfg-stats-scraper.onrender.com/your_username/card" 
         alt="GFG Stats Card"
         style="max-width: 500px;">
</body>
</html>
```

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)
- **Web Scraping:** Playwright
- **Browser Automation:** Browserless / Local Chromium
- **Deployment:** Render

---

## 📝 Notes

- All timestamps and dates are in UTC
- Profile data is scraped in real-time (not cached on server)
- SVG cards are cached for 4 hours
- Private profiles will return a 404 error
- Username is case-sensitive

---

## 🤝 Support

For issues or questions:
- Open an issue on GitHub
- Check `/docs` endpoint for interactive testing

---

## 📄 License

MIT License - feel free to use this API in your projects!

---

**Made with ❤️ using FastAPI and Playwright**
