export default function Page({ params }: { params: { id: string } }) {
  return (
    <div className="space-y-2">
      <h1 className="text-xl font-semibold">Cluster: {params.id}</h1>
      <p className="text-sm text-muted-foreground">Pain deep dive</p>
    </div>
  );
}
