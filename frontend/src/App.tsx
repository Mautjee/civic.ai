import "./App.css";
import { execHaloCmdWeb } from "@arx-research/libhalo/api/web";
import { Submit } from "./components/submit";
import { Button } from "./components/ui/button";
import { Textarea } from "./components/ui/textarea";
import Header from "./components/header";
import Noun from "./components/noun";

function App() {
  return (
    <div className="flex flex-col">
      <Header />
      <Noun/>
      <Textarea />
      <Button>Submit</Button>
    </div>
  );
}

export default App;
