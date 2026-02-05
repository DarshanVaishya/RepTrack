import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import API_BASE_URL from "../api";
import SelectInput from "../utils/SelectInput";
import TextInput from "../utils/TextInput";

export default function WorkoutEl() {
  const { workout_id } = useParams();
  const navigate = useNavigate()
  const [workout, setWorkout] = useState(null)
  const [exercises, setExercises] = useState(null)

  const [exercise_id, setExerciseId] = useState(null)
  const [notes, setNotes] = useState("")

  const [reps, setReps] = useState(0)
  const [weight, setWeight] = useState(0)
  const [set_type, setSetType] = useState("warmup")

  const [showSets, setShowSets] = useState(false)
  const [showExercise, setShowExercise] = useState(false)

  useEffect(() => {
    axios.get(`${API_BASE_URL}/workout/${workout_id}`).then(response => {
      setWorkout(response.data.data)
    })

    axios.get(`${API_BASE_URL}/exercises`).then(response => {
      setExercises(response.data.data)
    })
  }, [])

  const handleExerciseSubmit = async e => {
    e.preventDefault()
    await axios.post(`${API_BASE_URL}/workout/${workout_id}/exercise`, {
      exercise_id,
      order_index: 0,
      notes,
      workout_id
    })
    setExerciseId(null)
  }

  const handleSetSubmit = async e => {
    e.preventDefault()
    const response = await axios.post(`${API_BASE_URL}/workout/${workout_id}/exercise/${exercise_id}/set`, {
      reps,
      weight,
      set_type,
      order_index: 0,
      notes
    })
  }

  const handleStartSession = async e => {
    e.preventDefault()

    const response = await axios.post(`${API_BASE_URL}/sessions`, {
      workout_id,
      notes
    })
    const session_id = response.data.data.id
    navigate(`/sessions/${session_id}`)
  }

  if (workout == null)
    return <h1>Loading...</h1>

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold">{workout.name}</h1>
      {workout.notes && <h2>Notes: {workout.notes}</h2>}
      <input type="text" value={notes} onChange={e => setNotes(e.target.value)} />
      <button onClick={e => handleStartSession(e)}>Start session</button>

      <h3>Workout Exercises:</h3>
      {!workout.workout_exercises ? <p>No exercises for this workout.</p> :
        workout.workout_exercises.map(exercise => <div onClick={() => {
          setShowSets(true)
          setExerciseId(exercise.id)
        }} className="py-2 cursor-pointer bg-neutral-200 my-2" key={exercise.id}>
          <p>{exercise.exercise.name}</p>
          <p>Notes: {exercise.notes && exercise.notes}</p>
          <p>Sets:</p>
          {
            exercise.sets.map(set => <div key={set.id}>
              <div className="flex gap-5">
                <span>Reps: {set.reps}</span>
                <span>Weight: {set.weight}</span>
                <span className="capitalize">{set.set_type}</span>
              </div>
            </div>)
          }
        </div>)
      }


      {
        showSets && <div>
          <h3 className="mt-5 text-2xl">Add a workout set</h3>
          <form onSubmit={e => handleSetSubmit(e)}>
            <TextInput label="reps" value={reps} onChange={setReps} type="number" />
            <TextInput label="weight" value={weight} onChange={setWeight} type="number" />
            <SelectInput value={set_type} onChange={setSetType} label="Set Type">
              <option value="warmup">Warmup</option>
              <option value="normal">Normal</option>
              <option value="failure">Failure</option>
              <option value="dropset">Dropset</option>
            </SelectInput>
            <TextInput label="notes" value={notes} onChange={setNotes} />
            <button type="submit">Add</button>
          </form>
        </div>
      }



      <h3 className="mt-5 text-2xl">All Exercises</h3>
      {exercises.map(exercise => <div key={exercise.id}>
        <h4 className="cursor-pointer" onClick={() => {
          setExerciseId(exercise.id)
          setShowExercise(true)
        }}
        >{exercise.id} {exercise.name}</h4>
      </div>)}

      {showExercise && <>
        <h3 className="mt-5 text-2xl">Add a workout exercise</h3>
        <form onSubmit={e => handleExerciseSubmit(e)}>
          <input type="text" placeholder="notes" value={notes} onChange={e => setNotes(e.target.value)} />
          <button type="submit">Add</button>
        </form>
      </>}
    </div >
  );
}
