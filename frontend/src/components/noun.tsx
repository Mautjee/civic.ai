import { Nouns_API } from "@/constants";
import React from "react";

const Noun: React.FC<{}> = () => {
  return (
    <div>
      <div>
        <img height="250" src={Nouns_API} alt="Noun" />
      </div>
    </div>
  );
};
export default Noun;

