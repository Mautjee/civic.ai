import { useNouns } from "@/hooks/nouns";
import React from "react";


const Noun: React.FC<{}> = () => {
    const { data } = useNouns();
  return (
    <div>
      <div>
        <img height="250" src={data} alt="Noun" /> 
      </div>
    </div>
  );
};
export  default Noun;