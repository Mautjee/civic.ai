import "./App.css";
import { execHaloCmdWeb } from "@arx-research/libhalo/api/web";
import { Submit } from "./components/submit";

function App() {
  async function btnClick() {
    let command = {
      name: "sign",
      keyNo: 1,
      message: "010203",
    };

    let res;

    try {
      // --- request NFC command execution ---
      res = await execHaloCmdWeb(command);
      // the command has succeeded, display the result to the user
      console.log(JSON.stringify(res, null, 4));
    } catch (e) {
      // the command has failed, display error to the user
      console.log("Error: " + String(e));
    }
  }
  return (
    <div className="App">
      <div>
        <Submit />
      </div>
    </div>
  );
}

export default App;
