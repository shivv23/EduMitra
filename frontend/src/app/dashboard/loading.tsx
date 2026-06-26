export default function DashboardLoading() {
  return (
    <div className="min-h-screen bg-surface-950">
      <div className="h-16 bg-surface-900/50 border-b border-surface-800/50" />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
        <div className="skeleton h-8 w-64 mb-2" />
        <div className="skeleton h-4 w-48 mb-8" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[1,2,3,4].map(i => <div key={i} className="skeleton h-24 rounded-2xl" />)}
        </div>
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 skeleton h-80 rounded-2xl" />
          <div className="flex flex-col gap-6">
            <div className="skeleton h-64 rounded-2xl" />
            <div className="skeleton h-32 rounded-2xl" />
          </div>
        </div>
      </main>
    </div>
  );
}
