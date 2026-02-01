"use client";
import dynamic from "next/dynamic";
import { useState } from "react";
const ForceGraph2D = dynamic(
  () => import("react-force-graph-2d"),
  { ssr: false }
);
import { Share2 } from "lucide-react";

export default function FollowerNetwork({ data }) {
  const [hoverNode, setHoverNode] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const graphData ={
    nodes: data.nodes,
    links: data.links
  }
  return (
    <div className="relative bg-white rounded-3xl border border-slate-200 shadow-xl p-8 col-span-1 lg:col-span-2">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Share2 size={20} className="text-indigo-600" />
          <h3 className="font-black text-lg">Follower Ego Network</h3>
        </div>
        <span className="text-xs font-bold text-slate-400 uppercase">
          Interactive Node Map
        </span>
      </div>

      <div className="h-[500px] bg-slate-50 rounded-2xl overflow-hidden border border-slate-100">
        <ForceGraph2D
          graphData={graphData}
          nodeColor={(node) => node.color || "#4F46E5"}
          nodeVal={(node) => node.size || 10}
          linkColor={() => "#CBD5E1"}
          cooldownTicks={100}
          onNodeHover={(node, event) => {
            if (!node) {
              setHoverNode(null);
              return;
            }

            setHoverNode(node);
            setMousePos({
              x: event.clientX,
              y: event.clientY
            });
          }}
        />
      </div>

      {/* 🔹 TOOLTIP */}
      {hoverNode && (
        <div
          className="fixed z-50 pointer-events-none bg-slate-900 text-white text-xs rounded-xl shadow-xl px-4 py-3"
          style={{
            left: mousePos.x + 12,
            top: mousePos.y + 12
          }}
        >
          <p className="font-bold text-sm">@{hoverNode.id}</p>
          <p className="text-slate-300">
            Followers: {hoverNode.followers ?? "N/A"}
          </p>
          <p className="text-slate-300">
            Following: {hoverNode.following ?? "N/A"}
          </p>
          {hoverNode.verified && (
            <p className="text-emerald-400 font-semibold mt-1">
              ✔ Verified
            </p>
          )}
        </div>
      )}
    </div>
  );
}
