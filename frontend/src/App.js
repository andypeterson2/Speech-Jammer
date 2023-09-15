import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Start from "./screens/Start";
import Join from "./screens/Join";
import Session from "./screens/Session";

function App() {

    return (
        <Router>
            <Routes>
                {/* Host Video Session */}
                <Route path="/session/host/*" element={<Session host />}>
                </Route>

                {/* Client Video Session */}
                <Route path="/session/client/*" element={<Session client />}>
                </Route>

                {/* Join Session Prompt */}
                <Route path="/join" element={<Join />}>
                </Route>

                {/* Home Page */}
                <Route path="/*" element={<Start />}>
                </Route>
                
            </Routes>
        </Router>
    );
}

export default App;
