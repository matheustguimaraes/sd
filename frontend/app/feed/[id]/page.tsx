"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { productsApi } from "@/lib/api";
import Link from "next/link";
import PageLayout from "@/components/PageLayout";

export default function PostPage() {
  const params = useParams();
  const router = useRouter();
  const postId = parseInt(params.id as string);

  const { data: post, isLoading } = useQuery({
    queryKey: ["products", postId],
    queryFn: () => productsApi.get(postId),
  });

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-black">Carregando...</div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="flex flex-col items-center gap-4 text-center">
          <p className="text-black">Post não encontrado</p>
          <Link href="/feed" className="text-blue-600 hover:text-blue-800">
            Voltar ao feed
          </Link>
        </div>
      </div>
    );
  }

  return (
    <PageLayout
      leftElement={
        <button
          onClick={() => router.back()}
          className="text-black hover:text-black/70"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
      }
      rightElements={[
        <Link
          key="profile"
          href="/profile"
          className="text-black hover:text-black/70"
          title="Perfil"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
        </Link>,
      ]}
    >
      <div className="overflow-hidden rounded-lg border border-black">
            {post.image_url ? (
              <img
                src={post.image_url}
                alt={post.name || "Post"}
                className="w-full object-cover"
              />
            ) : post.thumbnail_url ? (
              <img
                src={post.thumbnail_url}
                alt={post.name || "Post"}
                className="w-full object-cover"
              />
            ) : (
              <div className="flex aspect-square w-full items-center justify-center bg-white border border-black">
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
              </div>
            )}

            {post.description && (
              <div className="border-t border-black p-4">
                <p className="text-black whitespace-pre-wrap">
                  {post.description}
                </p>
                {post.created_at && (
                  <p className="mt-2 text-xs text-black/60">
                    {new Date(post.created_at).toLocaleDateString("pt-BR", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })}
                  </p>
                )}
              </div>
            )}
          </div>
    </PageLayout>
  );
}

