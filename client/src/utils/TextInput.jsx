export default function TextInput({ label = "", type = "text", placeholder = "", value, onChange }) {
  return (
    <div className="flex flex-col items-baseline mb-2">
      <label className="capitalize">{label}</label>
      <input type={type} placeholder={placeholder || label} value={value} onChange={e => onChange(e.target.value)} />
    </div>
  )
}
