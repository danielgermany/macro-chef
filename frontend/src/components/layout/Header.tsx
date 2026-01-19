export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800">Macro Chef</h2>
        <div className="flex items-center space-x-4">
          {/* User info will go here in Phase 5 */}
          <span className="text-sm text-gray-600">User Profile</span>
        </div>
      </div>
    </header>
  );
}
