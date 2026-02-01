"use client";

import dynamic from "next/dynamic";
import { useState, useRef, useCallback, useEffect, useMemo } from "react";
import { Share2 } from "lucide-react";

const ForceGraph2D = dynamic(
  () => import("react-force-graph-2d"),
  { ssr: false }
);

export default function FollowerNetwork({ data }) {
  const fgRef = useRef();
  const [hoverNode, setHoverNode] = useState(null);
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());

  const processedData = useMemo(() => {
    if (!data || !data.nodes || !data.edges) return null;

    // Filter to show only the first 10 nodes (including the target)
    const limitedNodes = data.nodes.slice(0, 10);
    const nodeIds = new Set(limitedNodes.map(n => n.id));

    // Only keep edges where both source and target exist in our 10 nodes
    const limitedEdges = data.edges.filter(edge => 
      nodeIds.has(typeof edge.source === 'object' ? edge.source.id : edge.source) && 
      nodeIds.has(typeof edge.target === 'object' ? edge.target.id : edge.target)
    );

    return {
      nodes: limitedNodes,
      links: limitedEdges.map(edge => ({
        source: typeof edge.source === 'object' ? edge.source.id : edge.source,
        target: typeof edge.target === 'object' ? edge.target.id : edge.target
      }))
    };
  }, [data]);

  useEffect(() => {
    if (fgRef.current) {
      // Reduced repulsion for a smaller, tighter web
      fgRef.current.d3Force("charge").strength(-300);
      // Shorter link distance to pull nodes toward the center
      fgRef.current.d3Force("link").distance(80);
      fgRef.current.d3Force("center").strength(0.1);
    }
  }, [processedData]);

  const updateHighlight = (node) => {
    const nodes = new Set();
    const links = new Set();

    if (node && processedData) {
      nodes.add(node.id);
      processedData.links.forEach(link => {
        const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
        const targetId = typeof link.target === 'object' ? link.target.id : link.target;
        
        if (sourceId === node.id || targetId === node.id) {
          links.add(link);
          nodes.add(sourceId === node.id ? targetId : sourceId);
        }
      });
    }

    setHighlightNodes(nodes);
    setHighlightLinks(links);
  };

  const handleNodeHover = (node) => {
    setHoverNode(node);
    updateHighlight(node);
  };

  const handleEngineStop = useCallback(() => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400, 50);
    }
  }, []);

  if (!processedData) return null;

  return (
    <div className="relative bg-white rounded-3xl border border-slate-200 shadow-xl p-8 col-span-1 lg:col-span-2">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Share2 size={20} className="text-indigo-600" />
          <h3 className="font-black text-lg">Follower Ego Network (Top 10)</h3>
        </div>
      </div>

      <div className="h-[400px] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 cursor-crosshair relative">
        <ForceGraph2D
          ref={fgRef}
          graphData={processedData}
          nodeId="id"
          backgroundColor="#020617"
          showNavInfo={false}
          
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.id;
            const fontSize = 12 / globalScale;
            ctx.font = `${node === hoverNode ? '700' : '400'} ${fontSize}px Inter, Sans-Serif`;
            
            const isHighlighted = highlightNodes.size === 0 || highlightNodes.has(node.id);
            const alpha = isHighlighted ? 1 : 0.2;

            ctx.beginPath();
            ctx.arc(node.x, node.y, node.role === "target" ? 5 : 3, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.role === "target" ? `rgba(14, 165, 233, ${alpha})` : `rgba(16, 185, 129, ${alpha})`;
            ctx.fill();

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
            ctx.fillText(label, node.x, node.y + (node.role === "target" ? 10 : 8));
          }}

          linkCanvasObject={(link, ctx) => {
            const isHighlighted = highlightLinks.size === 0 || highlightLinks.has(link);
            ctx.strokeStyle = isHighlighted ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.05)';
            ctx.lineWidth = isHighlighted ? 1 : 0.5;
            ctx.beginPath();
            ctx.moveTo(link.source.x, link.source.y);
            ctx.lineTo(link.target.x, link.target.y);
            ctx.stroke();
          }}

          onNodeHover={handleNodeHover}
          onEngineStop={handleEngineStop}
        />

        {hoverNode && (
          <div className="absolute bottom-4 right-4 pointer-events-none bg-slate-900/95 border border-slate-700 p-3 rounded-xl shadow-2xl min-w-[150px]">
            <p className="font-black text-sm text-white">@{hoverNode.id}</p>
            <p className="text-xs text-sky-400 mt-1">
              Followers: <span className="font-bold">{hoverNode.followers?.toLocaleString() ?? "0"}</span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}