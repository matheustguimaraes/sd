"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { productsApi } from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";
import PageLayout from "@/components/PageLayout";

export default function FeedPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: posts, isLoading } = useQuery({
    queryKey: ["products"],
    queryFn: () => productsApi.list(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => productsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });

  const handleDelete = async (id: number) => {
    if (confirm("Tem certeza que deseja excluir este post?")) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-black">Carregando...</div>
      </div>
    );
  }

  return (
    <PageLayout
      leftElement={<h1 className="text-xl font-bold text-black">SD Insta</h1>}
    >
      {posts && posts.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-center">
              <svg
                className="h-16 w-16 text-black/30"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p className="mt-4 text-black">Nenhum post ainda</p>
              <Link
                href="/feed/new"
                className="mt-4 rounded-lg bg-black px-6 py-2 text-white hover:bg-black/90"
              >
                Fazer primeiro post
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {posts?.map((post) => (
                <div
                  key={post.id}
                  className="group relative flex aspect-square w-full overflow-hidden rounded-lg border border-black"
                >
                  {post.thumbnail_url ? (
                    <img
                      src={post.thumbnail_url}
                      alt={post.name || "Post"}
                      className="h-full w-full object-cover"
                    />
                  ) : post.image_url ? (
                    <img
                      src={post.image_url}
                      alt={post.name || "Post"}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center bg-white border border-black">
                      <svg
                        className="h-12 w-12 text-black/30"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                    </div>
                  )}
                  <div className="absolute inset-0 flex items-center justify-center gap-4 bg-black/0 transition-all group-hover:bg-black/50">
                    <button
                      onClick={() => router.push(`/feed/${post.id}`)}
                      className="rounded-full bg-white px-4 py-2 text-sm font-medium text-black opacity-0 transition-opacity group-hover:opacity-100"
                    >
                      Ver
                    </button>
                    <button
                      onClick={() => handleDelete(post.id)}
                      className="rounded-full bg-white px-4 py-2 text-sm font-medium text-red-600 opacity-0 transition-opacity group-hover:opacity-100"
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
    </PageLayout>
  );
}
