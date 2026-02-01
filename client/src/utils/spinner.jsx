import { Loader, LoaderCircle } from "lucide-react"

export default function Spinner({ size = 32 }) {
  return (
    <LoaderCircle className="animate-spin text-2xl" size={32} />
  )
}
