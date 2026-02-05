import { useEffect, useState } from "react";
import SessionSetEl from "./SessionSetEl";
import API_BASE_URL from "../api";
import axios from "axios";
import Spinner from "./spinner";

export default function SessionExerciseEl({ sessionExercise, workout_id, session_id }) {
  const [exercise, setExercise] = useState(null)

  useEffect(() => {
    axios.get(`${API_BASE_URL}/workout/${workout_id}/exercise/${sessionExercise.workout_exercise_id}`)
      .then(response =>
        setExercise(response.data.data.exercise)
      )
  }, [])

  return (
    <div className="p-5 bg-gray-100 my-2" key={sessionExercise.id}>
      <p>{exercise ? exercise.name : <Spinner />}</p>
      <p>Note: {sessionExercise.notes}</p>
      {sessionExercise.session_sets.map(s => <div key={s.id}>
        <p>Set {s.id}</p>
        <SessionSetEl set={s} session_id={session_id} />
      </div>)}
    </div>
  )
}
