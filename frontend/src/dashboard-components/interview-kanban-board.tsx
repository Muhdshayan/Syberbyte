import { useState } from "react";
import InterviewCard from "@/dashboard-components/interview-cards";
import ActiveScreeningNotes from "@/dashboard-components/active-screening-notes";
import { DndContext, closestCenter } from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useDroppable, useDraggable } from "@dnd-kit/core";

// Draggable InterviewCard wrapper
function DraggableInterviewCard({ id, card, index }: any) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id,
  });

  return (
    <div
      ref={setNodeRef}
      style={{
        opacity: isDragging ? 0.5 : 1,
        transform: transform
          ? `translate3d(${transform.x}px, ${transform.y}px, 0)`
          : undefined,
        cursor: "grab",
      }}
      {...attributes}
      {...listeners}
    >
      <InterviewCard name={card.name} time={card.time} role={card.role} />
    </div>
  );
}

// Droppable column wrapper
function DroppableColumn({ id, title, cards, children }: any) {
  const { setNodeRef, isOver } = useDroppable({ id });
  return (
    <div
      ref={setNodeRef}
      className={`bg-white rounded-lg border p-4 flex-1 min-w-[200px] transition-all ${
        isOver ? "ring-2 ring-blue-400" : ""
      }`}
    >
      <div className="font-poppins-semibold text-xl text-left mb-4">{title}</div>
      {children}
    </div>
  );
}

const initialData = {
  upcoming: [
    { id: "c3", name: "Candidate 3", time: "June 13 10:20AM", role: "Frontend Developer" },
    { id: "c4", name: "Candidate 4", time: "June 13 10:30AM", role: "Frontend Developer" },
  ],
  inProgress: [
    { id: "c2", name: "Candidate 2", time: "June 13 10:10AM", role: "Frontend Developer" },
  ],
  completed: [
    { id: "c1", name: "Candidate 1", time: "June 13 10:00AM", role: "Frontend Developer" },
  ],
};

export default function InterviewKanbanBoard() {
  const [columns, setColumns] = useState(initialData);

  function handleDragEnd(event: any) {
    const { active, over } = event;
    if (!over) return;

    // Find source and destination columns
    let sourceCol: keyof typeof columns | null = null;
    let destCol: keyof typeof columns | null = null;
    Object.keys(columns).forEach((col) => {
      if (columns[col as keyof typeof columns].find((c) => c.id === active.id)) {
        sourceCol = col as keyof typeof columns;
      }
      if (col === over.id) {
        destCol = col as keyof typeof columns;
      }
    });

    if (!sourceCol || !destCol) return;
    if (sourceCol === destCol) return;

    // Move card from sourceCol to destCol
    const card = columns[sourceCol].find((c) => c.id === active.id);
    if (!card) return;
    setColumns((prev) => ({
      ...prev,
      [sourceCol!]: prev[sourceCol!].filter((c) => c.id !== active.id),
      [destCol!]: [card, ...prev[destCol!]],
    }));
  }

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <div className="flex md:flex-row flex-col justify-center gap-4 w-full">
        {/* Kanban Columns */}
        <div className="flex md:flex-row flex-col flex-1 gap-4 md:w-[70%]">
          <DroppableColumn id="upcoming" title="Upcoming" cards={columns.upcoming}>
            {columns.upcoming.map((c, i) => (
              <DraggableInterviewCard key={c.id} id={c.id} card={c} index={i} />
            ))}
          </DroppableColumn>
          <DroppableColumn id="inProgress" title="In-Progress" cards={columns.inProgress}>
            {columns.inProgress.map((c, i) => (
              <DraggableInterviewCard key={c.id} id={c.id} card={c} index={i} />
            ))}
          </DroppableColumn>
          <DroppableColumn id="completed" title="Completed" cards={columns.completed}>
            {columns.completed.map((c, i) => (
              <DraggableInterviewCard key={c.id} id={c.id} card={c} index={i} />
            ))}
          </DroppableColumn>
        </div>
        {/* Active Screening Notes */}
        <ActiveScreeningNotes />
      </div>
    </DndContext>
  );
}