import { useEffect, useState } from "react";
import Container from "../utils/container";
import Spinner from "../utils/spinner";
import axios from "axios";
import API_BASE_URL from "../api";
import TextInput from "../utils/TextInput";
import SelectInput from "../utils/SelectInput";

export default function ExercisesEl() {
  const [exercises, setExercises] = useState(null)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [muscle_group, setMuscleGroup] = useState("chest")
  const [equipment, setEquipment] = useState("barbell")

  useEffect(() => {
    axios.get(`${API_BASE_URL}/exercises`).then(response =>
      setExercises(response.data.data)
    )
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const response = await axios.post(`${API_BASE_URL}/exercises`, {
      name,
      description,
      muscle_group,
      equipment
    })

    setExercises([...exercises, response.data.data])
  }

  return (
    <Container>
      <h2 className="text-2xl">Create Exercise</h2>
      <form onSubmit={e => handleSubmit(e)}>
        <TextInput label="name" value={name} onChange={setName} />
        <TextInput label="description" value={description} onChange={setDescription} />
        <SelectInput label="Muscle Group" value={muscle_group} onChange={setMuscleGroup}>
          <option value="chest">Chest</option>
          <option value="back">Back</option>
          <option value="shoulders">Shoulders</option>
          <option value="arms">Arms</option>
          <option value="legs">Legs</option>
          <option value="core">Core</option>
          <option value="calves">Calves</option>
          <option value="full_body">Full Body</option>
        </SelectInput>
        <SelectInput label="Eqipment" value={equipment} onChange={setEquipment}>
          <option value="barbell">Barbell</option>
          <option value="dumbbells">Dumbbells</option>
          <option value="cable_machine">Cable Machine</option>
          <option value="machine">Machine</option>
          <option value="bodyweight">Bodyweight</option>
          <option value="kettlebell">Kettlebell</option>
          <option value="medicine_ball">Medicine Ball</option>
          <option value="resistance_band">Resistance Band</option>
          <option value="cardio">Cardio</option>
        </SelectInput>
        <button type="submit">Submit</button>
      </form>
      <h1 className="text-2xl mt-5">All Exercises</h1>
      {
        exercises != null ?
          <div>
            {exercises.map(e => <p key={e.id}>{e.name}</p>)}
          </div>
          : <Spinner />
      }
    </Container>
  )
}
