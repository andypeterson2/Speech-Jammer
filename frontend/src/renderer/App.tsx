import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Start from "./screens/Start";
import Join from "./screens/Join";
import Session from "./screens/Session";

export default function App() {
	const statuses = ["waiting", "good", "bad"];
	const status = statuses[0];

	return (
		<Router>
			<Routes>
				{/* Host Video Session */}
				<Route
					path="/session/host/*"
					element={<Session host status={status} />}
				/>

				{/* Client Video Session */}
				<Route
					path="/session/client/*"
					element={<Session status={status} />}
				/>

				{/* Join Session Prompt */}
				<Route path="/join" element={<Join />}/>

				{/* Home Page */}
				<Route path="/*" element={<Start />}/>
			</Routes>
		</Router>
	);
}
