"use client";

import { useEffect, useState } from "react";

import { getMe, listMembers } from "@/lib/api/sessions";
import type { Member } from "@/lib/api/types";
import { useToken } from "@/lib/use-token";

export default function MembersPage() {
  const getToken = useToken();
  const [members, setMembers] = useState<Member[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const token = await getToken();
        const me = await getMe(token);
        const orgId = me.memberships[0]?.org.id;
        if (!orgId) {
          if (active) setMembers([]);
          return;
        }
        const data = await listMembers(token, orgId);
        if (active) setMembers(data);
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load members.");
        }
      }
    })();
    return () => {
      active = false;
    };
  }, [getToken]);

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-6 text-xl font-semibold">Members</h1>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {!error && members === null && (
        <p className="text-sm text-muted-foreground">Loading…</p>
      )}
      {members?.length === 0 && (
        <p className="text-sm text-muted-foreground">No members found.</p>
      )}

      <table className="w-full text-sm">
        <thead className="text-left text-muted-foreground">
          <tr className="border-b">
            <th className="py-2 font-medium">Email</th>
            <th className="py-2 font-medium">Name</th>
            <th className="py-2 font-medium">Role</th>
          </tr>
        </thead>
        <tbody>
          {members?.map((member) => (
            <tr key={member.id} className="border-b">
              <td className="py-2">{member.user.email}</td>
              <td className="py-2">{member.user.name ?? "—"}</td>
              <td className="py-2">{member.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
