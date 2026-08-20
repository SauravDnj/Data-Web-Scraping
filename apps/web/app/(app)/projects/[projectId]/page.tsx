"use client";

import { use } from "react";
import { ProjectDetailView } from "@/components/projects/ProjectDetailView";

export default function ProjectDetailPage(
  props: PageProps<"/projects/[projectId]">,
) {
  const { projectId } = use(props.params);
  return <ProjectDetailView projectId={Number(projectId)} />;
}
