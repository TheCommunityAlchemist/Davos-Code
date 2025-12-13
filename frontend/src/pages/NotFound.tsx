import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a1628]">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-cyan-400 mb-4">404</h1>
        <p className="text-xl text-slate-400 mb-8">
          Page not found
        </p>
        <Button asChild className="bg-gradient-to-br from-cyan-400 to-emerald-500 text-[#0a1628]">
          <Link to="/">Return to Navigator</Link>
        </Button>
      </div>
    </div>
  );
}
