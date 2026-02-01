export default function SelectInput({ label = "", type = "text", placeholder = "", value, onChange, children }) {
  return (
    <div className="flex flex-col items-baseline mb-2">
      <label className="capitalize">{label}</label>
      <select value={value} onChange={e => onChange(e.target.value)}>
        {children}
      </select>
    </div>
  )
}
