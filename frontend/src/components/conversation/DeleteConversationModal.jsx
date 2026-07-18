import Modal from '../ui/Modal';
import Button from '../ui/Button';

export default function DeleteConversationModal({ isOpen, onClose, onConfirm, deleting, conversationTitle }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Delete Conversation?">
      <div className="space-y-4">
        <p className="text-sm text-slate-500 leading-relaxed">
          Are you sure you want to delete <span className="font-semibold text-slate-800">"{conversationTitle}"</span>? This action cannot be undone, and all message history will be permanently erased.
        </p>
        <div className="flex justify-end gap-3 pt-2">
          <Button
            onClick={onClose}
            disabled={deleting}
            variant="secondary"
            className="px-4 py-2 font-semibold h-10 cursor-pointer"
          >
            Cancel
          </Button>
          <Button
            onClick={onConfirm}
            disabled={deleting}
            className="px-4 py-2 font-semibold h-10 cursor-pointer bg-rose-600 hover:bg-rose-500 active:bg-rose-700 text-white"
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
