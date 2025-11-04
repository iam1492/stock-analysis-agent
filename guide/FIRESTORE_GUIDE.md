* Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
* TODO: Add SDKs for Firebase products that you want to use
* https://firebase.google.com/docs/web/setup#available-libraries

* Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDZpb_uTG95YAWbcQXZcDyMO2ySjua6rMA",
  authDomain: "stock-analysis-agent-a7bff.firebaseapp.com",
  projectId: "stock-analysis-agent-a7bff",
  storageBucket: "stock-analysis-agent-a7bff.firebasestorage.app",
  messagingSenderId: "38726995691",
  appId: "1:38726995691:web:f7f415d48dd657be2938ae"
};

* Initialize Firebase
const app = initializeApp(firebaseConfig);

* firestore 구조

/stock_agents/{agent_name}
    - llm_model: "gemini-2.5-flash"

# Ex. firestore 예시 구조
stock_agents(container)/income_statement_agent(document_id) - llm_model(key):"gemini-2.5-flash"(value)
stock_agents(container)/hedge_fund_manager_agent(document_id) - llm_model(key):"gemini-2.5-pro"(value)

# Ex. 예시 코드
```typescript
import { db } from '../lib/firebase'; // Adjust path as needed
import { collection, getDocs } from 'firebase/firestore';
// ...
async function fetchAgents() {
  const querySnapshot = await getDocs(collection(db, "stock_agents"));
  const agents = querySnapshot.docs.map(doc => ({
    agent_name: doc.id,
    ...doc.data()
  }));
  console.log(agents);
  return agents;
}
```