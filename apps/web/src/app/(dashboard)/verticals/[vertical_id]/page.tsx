export default function Page({ params }: { params: { vertical_id: string } }) {
  return (
    <div className="space-y-2">
      <h1 className="text-xl font-semibold">Vertical: {params.vertical_id}</h1>
      <p className="text-sm text-muted-foreground">Vertical deep dive</p>
    </div>
  );
}
