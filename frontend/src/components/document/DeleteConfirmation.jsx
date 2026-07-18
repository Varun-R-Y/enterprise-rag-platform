import Button from '../ui/Button';

export default function DeleteConfirmation({ filename, onCancel, onConfirm, isDeleting }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-600 leading-relaxed">
        Are you sure you want to delete <span className="font-semibold text-slate-800">"{filename}"</span>?
        This action will permanently remove the document and its vector representations from the system. This cannot be undone.
      </p>
      <div className="flex items-center justify-end gap-3 pt-2">
        <Button
          onClick={onCancel}
          variant="secondary"
          disabled={isDeleting}
          className="h-10 px-4 py-2 cursor-pointer"
        >
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          disabled={isDeleting}
          className="bg-rose-600 hover:bg-rose-500 active:bg-rose-700 text-white border border-transparent shadow-sm h-10 px-4 py-2 cursor-pointer focus:ring-rose-500 focus:ring-offset-2"
        >
          {isDeleting ? 'Deleting...' : 'Delete'}
        </Button>
      </div>
    </div>
  );
}
