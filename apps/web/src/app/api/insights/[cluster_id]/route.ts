import { NextRequest } from "next/server";

export async function GET(
  req: NextRequest,
  { params }: { params: { cluster_id: string } }
) {
  const backend = process.env.BACKEND_URL || "http://localhost:8000";
  const url = `${backend}/insights/${params.cluster_id}`;

  const res = await fetch(url);
  const data = await res.json();

  return Response.json(data);
}
