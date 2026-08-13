import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search } from "lucide-react";

import { verifyQuestion } from "../../api/query";
import PrimaryButton from "../ui/PrimaryButton";

export default function QueryBox() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  async function handleVerify() {
    if (!question.trim()) return;

    try {
      setLoading(true);

      const result = await verifyQuestion(question);

      navigate(`/result/${result.record_id}`);
    } 
    
    catch (err: any) {
    console.error(err);

    if (err.response) {
        console.log("Status:", err.response.status);
        console.log("Data:", err.response.data);
        alert(JSON.stringify(err.response.data, null, 2));
    } 
    else {
        alert(err.message);
    }
    }

    finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-14 w-full max-w-4xl">

      <div className="rounded-2xl border border-white/10 bg-[#121216] p-3">

        <div className="flex items-center gap-4">

          <Search className="text-zinc-500" />

          <textarea
            rows={1}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a factual question..."
            className="
            flex-1
            resize-none
            bg-transparent
            outline-none
            text-lg
            text-white
            "
          />

          <PrimaryButton
            loading={loading}
            onClick={handleVerify}
          >
            Verify
          </PrimaryButton>

        </div>

      </div>

    </div>
  );
}