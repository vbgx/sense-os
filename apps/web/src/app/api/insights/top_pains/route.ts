import { NextRequest } from "next/server";

export async function GET(req: NextRequest) {
  const backend = process.env.BACKEND_URL || "http://localhost:8000";
  const url = `${backend}/insights/top_pains?${req.nextUrl.searchParams.toString()}`;

  const res = await fetch(url);
  const data = await res.json();

  return Response.json(data);
}
