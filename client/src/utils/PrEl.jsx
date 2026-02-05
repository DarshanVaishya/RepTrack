import { useEffect, useState } from "react"
import Spinner from "./spinner"
import axios from "axios"
import API_BASE_URL from "../api"
import { Trophy } from "lucide-react"

const mapPrType = {
  "max_volume": "Max Volume",
  "max_single_set": "Max Single Set",
  "max_weight": "Max Weight",
  "max_reps": "Max Reps"
}

export default function PrEl({ session_id }) {
  const [prs, setPrs] = useState(null)

  useEffect(() => {
    axios.get(`${API_BASE_URL}/prs?session_id=${session_id}`).then(response => {
      const prs = response.data.data
      setPrs(prs)
    })
  }, [])


  return (
    <>
      <h2 className="mt-5 text-xl font-bold">Personal Records Achieved ({prs?.length})</h2>
      {
        prs == null ?
          <Spinner />
          :
          <div>
            {
              prs.length == 0 ?
                <h3>None</h3>
                :
                <>
                  {prs.map(pr => <>
                    {<p className="flex gap-2 items-center">
                      <Trophy className="text-yellow-500" />  <b>{mapPrType[pr.pr_type]}:</b> {pr.exercise_name}
                    </p>}
                  </>)}
                </>
            }
          </div>
      }
    </>
  )
}
