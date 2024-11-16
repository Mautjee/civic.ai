import "./App.css";
import { Submit } from "@/components/submit";

function App() {
  return (
    <div className="flex flex-col overflow-auto min-h-screen flex-grow">
      <div className="flex-grow">
        <div className="mx-auto p-3 max-w-[1440px] md:px-[70px]">
          <Submit />
        </div>
      </div>
    </div>
  );
}

export default App;
